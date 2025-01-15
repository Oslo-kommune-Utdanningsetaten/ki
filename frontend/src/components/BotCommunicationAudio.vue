<script setup>
import { ref, useTemplateRef, watch, onMounted, onBeforeUnmount, onUpdated } from 'vue'
import BotAvatar from '@/components/BotAvatar.vue'
import ConversationSimple from '@/components/ConversationSimple.vue'
import AudioWave from '@/components/AudioWave.vue'
import workletURL from '../utils/pcm-processor.js?url'
import {
  languageOptions,
  getSelectedLanguage,
  getSelectedVoice,
  getVoicesForLanguage,
  updateLanguagePreferences,
} from '../utils/audioOptions.js'

// currentServerStatus is one of: 'websocketOpened', 'websocketClosed', 'initializing', 'receivingAudioFromClient', 'streamingTextToClient', 'generatingChatResponse', 'generatingAudioResponse', 'streamingAudioToClient', 'idle'

const props = defineProps({
  bot: {
    type: Object,
    required: true,
  },
  systemPrompt: {
    type: String,
  },
})

const websocketUrl = 'ws://localhost:5000/ws/audio/'
const isMicRecording = ref(false)
const isBotSpeaking = ref(false)
const isLanguageOptionsVisible = ref(false)
const currentServerStatus = ref('')
const messages = ref([])
const selectedLanguage = ref(getSelectedLanguage())
const selectedVoice = ref(getSelectedVoice(selectedLanguage.value))
const availableVoices = ref(getVoicesForLanguage(selectedLanguage.value))
const pageBottom = useTemplateRef('page-bottom-ref')

let intentionalShutdown = false

let microphonePermissionStatus = ref('denied')
let audioContext
let audioSource
let websocket

const handleToggleRecording = () => {
  // start and stop functions handle toggling of isMicRecording.value
  if (!isMicRecording.value) {
    startRecording()
  } else {
    stopRecording()
  }
}

const handleTogglePlayback = () => {
  console.info('handleTogglePlayback')
  if (isBotSpeaking.value) {
    audioSource.stop()
  } else {
    //isMicRecording.value = true
  }
}

const handleToggleLanguageOptions = () => {
  isLanguageOptionsVisible.value = !isLanguageOptionsVisible.value
}

const resetConversation = () => {
  messages.value = [
    {
      role: 'system',
      content: props.systemPrompt,
    },
  ]
}

const initializeWebsocket = async options => {
  const { shouldAutostartRecording } = options

  if (audioContext) {
    await audioContext.close()
  }
  audioContext = null

  const audioChunks = []
  websocket = new WebSocket(websocketUrl)

  websocket.onopen = () => {
    console.info('WebSocket opened')

    // send server configuration
    sendServerConfig()

    // send initial messages
    websocket.send(
      JSON.stringify({
        type: 'websocket.text',
        messages: messages.value,
      })
    )
  }

  websocket.onclose = () => {
    console.warn('WebSocket closed while', currentServerStatus.value)
    isBotSpeaking.value = false
    isMicRecording.value = false
    if (
      ['streamingAudioToClient', 'receivingAudioFromClient'].includes(currentServerStatus.value)
    ) {
      // socket closed unexpectedly while streaming, try to reconnect
      console.info('Will attempt to reconnect')
      initializeWebsocket({ shouldAutostartRecording: !intentionalShutdown })
      intentionalShutdown = false
    }
  }

  websocket.onmessage = event => {
    if (typeof event.data === 'string') {
      // server is updating messages or reporting on its status
      const { type, command, serverStatus, messages: updatedMessages } = JSON.parse(event.data)
      if (type === 'websocket.text' && updatedMessages) {
        messages.value = [...updatedMessages]
        scrollTo(pageBottom)
      }
      if (serverStatus) {
        console.info('Server status:', serverStatus)
        currentServerStatus.value = serverStatus
        if (!['idle', 'receivingAudioFromClient'].includes(serverStatus)) {
          isMicRecording.value = false
        }
      }
      if (type === 'websocket.audio') {
        if (command === 'audio-stream-begin') {
          // turn off mic while bot is speaking
          isMicRecording.value = false
          // start of audio stream, clear any lingering audio data
          audioChunks.length = 0
        } else if (command === 'audio-stream-end') {
          playAudioResponse(audioChunks)
        }
      }
    } else {
      // received audio data, store it for later playback
      audioChunks.push(event.data)
    }
  }

  if (shouldAutostartRecording) {
    console.warn('initializeWebsocket with AUTOSTART')
    await startRecording()
  }
}

const startRecording = async () => {
  isMicRecording.value = true
  // Get audio stream
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

  // Create a temp audio context to get the sample rate
  const audioContextTemp = new AudioContext()
  const sampleRate = audioContextTemp.sampleRate
  audioContextTemp.close()

  audioContext = new AudioContext({ sampleRate })

  // Load the AudioWorkletProcessor
  await audioContext.audioWorklet.addModule(workletURL)

  // Create MediaStreamSource and AudioWorkletNode
  const audioSourceNode = audioContext.createMediaStreamSource(stream)
  const workletNode = new AudioWorkletNode(audioContext, 'pcm-processor')
  // Connect the audioSourceNode to the worklet for processing
  audioSourceNode.connect(workletNode)

  // When workletNode is done processing an audio data chunk from the input stream, send to websocket
  workletNode.port.onmessage = event => {
    const pcmData = event.data // This should now be PCM data, 16kHz, 16bit, mono
    if (websocket.readyState === WebSocket.OPEN && isMicRecording.value) {
      websocket.send(pcmData)
    }
  }
}

const stopRecording = async () => {
  console.info('stopRecording')
  isMicRecording.value = false
  isBotSpeaking.value = false
  intentionalShutdown = true
  await websocket.close()
}

const playAudioResponse = async audioChunks => {
  if (audioChunks.length === 0) {
    return
  }

  // Create a blob with the correct MIME type
  const audioBlob = new Blob(audioChunks, { type: 'audio/mpeg' })
  const arrayBuffer = await audioBlob.arrayBuffer()

  if (audioContext.state === 'suspended') {
    await audioContext.resume()
  }

  audioContext.decodeAudioData(
    arrayBuffer,
    audioBuffer => {
      isBotSpeaking.value = true
      audioSource = audioContext.createBufferSource()
      audioSource.buffer = audioBuffer
      audioSource.onended = onAudioPlaybackFinished
      audioSource.connect(audioContext.destination)
      audioSource.start(0)
    },
    error => {
      console.error('Error while decoding audio data', error)
    }
  )
}

const onAudioPlaybackFinished = () => {
  console.info('Audio playback finished')
  isBotSpeaking.value = false
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    isMicRecording.value = true
  }
}

const sendServerConfig = () => {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    websocket.send(
      JSON.stringify({
        type: 'websocket.text',
        selected_language: selectedLanguage.value,
        selected_voice: selectedVoice.value,
        bot_uuid: props.bot.uuid,
        bot_model: props.bot.model,
      })
    )
  }
}

const checkMicrophonePermissionStatus = async () => {
  const permission = await navigator.permissions.query({ name: 'microphone' })
  microphonePermissionStatus.value = permission.state
}

const scrollTo = view => {
  view.value?.scrollIntoView({ block: 'end', behavior: 'smooth' })
}

// watch for changes in selectedLanguage or selectedVoice
watch([selectedLanguage, selectedVoice], () => {
  updateLanguagePreferences({
    selectedLanguage: selectedLanguage.value,
    selectedVoice: selectedVoice.value,
  })
  selectedVoice.value = getSelectedVoice(selectedLanguage.value)
  availableVoices.value = getVoicesForLanguage(selectedLanguage.value)
  sendServerConfig()
})

onMounted(() => {
  resetConversation()
  checkMicrophonePermissionStatus()
  initializeWebsocket({ shouldAutostartRecording: false })
})

onBeforeUnmount(() => {
  websocket.close()
})
</script>

<template>
  <div class="border">
    <ConversationSimple
      v-if="messages.length > 1"
      :messages="messages"
      :bot="props.bot"
      class="border-bottom"
    />

    <div class="px-5 pt-4 pb-2 d-flex justify-content-between">
      <div>
        <!-- Avatar playback state and control -->
        <button
          @click="handleTogglePlayback"
          class="audio-control-button me-4"
          :class="{ 'audio-control-button-stop': isBotSpeaking }"
          :title="isBotSpeaking ? 'Trykk for å pause bablinga' : 'Stille som en mus'"
          :disabled="microphonePermissionStatus === 'denied'"
        >
          <AudioWave v-if="isBotSpeaking" />
          <BotAvatar v-else :avatar_scheme="props.bot.avatar_scheme" />
        </button>

        <button
          class="btn oslo-btn-secondary mt-2 me-auto ps-1 pe-1 pt-0 pb-0"
          @click="handleToggleLanguageOptions"
          :class="{ 'oslo-btn-secondary-checked': isLanguageOptionsVisible }"
        >
          {{ isLanguageOptionsVisible ? 'Skjul' : 'Vis' }} språkvalg
        </button>

        <div class="container border" v-if="isLanguageOptionsVisible">
          <label for="language">Språk</label>
          <select v-model="selectedLanguage" class="form-select" @input="handleFormEdited">
            <option
              v-for="language in languageOptions.languages"
              :key="language.code"
              :value="language.code"
            >
              {{ language.name }}
            </option>
          </select>

          <label for="voice">Stemme</label>
          <select v-model="selectedVoice" class="form-select">
            <option v-for="voice in availableVoices" :key="voice.code" :value="voice.code">
              {{ voice.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- User record state and control -->
      <div>
        <button
          @click="handleToggleRecording"
          class="audio-control-button"
          :class="{ 'audio-control-button-stop': isMicRecording }"
          :title="
            microphonePermissionStatus === 'denied'
              ? 'Nettleseren har ikke tilgang til mikrofonen'
              : isMicRecording
                ? 'Trykk for å stoppe innspilling'
                : 'Trykk for å snakke'
          "
          :disabled="microphonePermissionStatus === 'denied'"
        >
          <AudioWave v-if="isMicRecording" />
          <img v-else src="@/components/icons/microphone.svg" class="mic-icon" alt="mikrofon" />
        </button>
      </div>
    </div>
  </div>
  <div ref="page-bottom-ref">&nbsp;</div>
</template>

<style>
.audio-control-button {
  position: relative;
  pointer-events: auto;
  height: 120px;
  width: 120px;
  border-radius: 50%;
  border: none;
  background-color: rgba(220, 220, 220, 0.5);
  transition: box-shadow 0.1s ease-in-out;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;

  svg {
    width: 55px;
    padding: auto;
  }

  .mic-icon {
    width: 80%;
  }
}

.audio-control-button:hover {
  box-shadow: 0px 0px 6px 4px rgba(45, 45, 45, 0.25);
  border-radius: 50%;
}

.audio-control-button-stop:hover::after {
  content: '×';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 18rem;
  opacity: 0.4;
  transition: opacity 0.25s ease;
  z-index: 10;
}

/* Optional: fade in animation */
.audio-control-button::after {
  opacity: 0;
}
</style>
