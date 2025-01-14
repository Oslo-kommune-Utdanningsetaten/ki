<script setup>
import { ref, useTemplateRef, watch, onMounted, onBeforeUnmount } from 'vue'
import BotAvatar from '@/components/BotAvatar.vue'
import ConversationSimple from '@/components/ConversationSimple.vue'
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
const serverStatusHistory = ref([])
const currentServerStatus = ref('')
const messages = ref([])
const selectedLanguage = ref(getSelectedLanguage())
const selectedVoice = ref(getSelectedVoice(selectedLanguage.value))
const availableVoices = ref(getVoicesForLanguage(selectedLanguage.value))
const conversationWidgets = useTemplateRef('conversation-widgets')

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

const resetConversation = () => {
  messages.value = [
    {
      role: 'system',
      content: props.systemPrompt,
    },
    { role: 'user', content: 'What is sugar' },
    { role: 'assistant', content: 'Sugar is sweet' },
    { role: 'user', content: 'Are you sure?' },
    { role: 'assistant', content: 'Sorry for the confusion, no' },
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
    console.warn('WebSocket closed - server is', currentServerStatus.value)
    isBotSpeaking.value = false
    isMicRecording.value = false
    if (
      ['streamingAudioToClient', 'receivingAudioFromClient'].includes(currentServerStatus.value)
    ) {
      // socket closed unexpectedly while streaming, try to reconnect
      console.info('Unexpected closing of websocket, will attempt to reconnect')
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
        scrollTo(conversationWidgets)
      }
      if (serverStatus) {
        console.info('Server status:', serverStatus)
        serverStatusHistory.value.push(serverStatus)
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
      audioSource = audioContext.createBufferSource()
      audioSource.buffer = audioBuffer
      audioSource.connect(audioContext.destination)
      isBotSpeaking.value = true
      audioSource.start(0)
      audioSource.onended = onAudioPlaybackFinished
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
  <ConversationSimple :messages="messages" :bot="props.bot" />

  <div ref="conversation-widgets" class="border p-3 mb-3 container">
    <div class="row g-6">
      <div class="col-4 border">
        <!-- Avatar playback state and control -->
        <button
          @click="handleTogglePlayback"
          class="audio-control-button me-4"
          :class="isBotSpeaking ? 'speakingAvatar' : 'silentAvatar'"
          :title="isBotSpeaking ? 'Trykk for å pause bablinga' : 'Stille som en mus'"
          :disabled="microphonePermissionStatus === 'denied'"
        >
          <div class="bot-button-avatar">
            <BotAvatar :avatar_scheme="props.bot.avatar_scheme" />
          </div>
        </button>

        <div class="container">
          <div class="row">
            <div class="col-4"><label for="language">Språk</label></div>
            <div class="col-4">
              <select v-model="selectedLanguage" class="form-select" @input="handleFormEdited">
                <option
                  v-for="language in languageOptions.languages"
                  :key="language.code"
                  :value="language.code"
                >
                  {{ language.name }}
                </option>
              </select>
            </div>
          </div>
          <div class="row">
            <div class="col-4"><label for="voice">Stemme</label></div>
            <div class="col-4">
              <select v-model="selectedVoice" class="form-select">
                <option v-for="voice in availableVoices" :key="voice.code" :value="voice.code">
                  {{ voice.name }}
                </option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- User record state and control -->
      <div class="col-4 border">
        <button
          @click="handleToggleRecording"
          class="audio-control-button"
          :class="isMicRecording ? 'speakingUserZ' : 'silentUserZ'"
          :title="
            microphonePermissionStatus === 'denied'
              ? 'Nettleseren har ikke tilgang til mikrofonen'
              : isMicRecording
                ? 'Trykk for å stoppe innspilling'
                : 'Trykk for å snakke'
          "
          :disabled="microphonePermissionStatus === 'denied'"
        >
          <img src="@/components/icons/microphone.svg" class="mic-icon" alt="mikrofon" />
        </button>
      </div>
    </div>
  </div>

  <!-- Filter for creating the glowing microphone effect -->
  <svg height="0" width="0" style="position: absolute; overflow: hidden">
    <defs>
      <filter id="shadow" color-interpolation-filters="sRGB">
        <feDropShadow dx="0" dy="0" flood-color="#eb0000" flood-opacity="0" stdDeviation="10">
          <animate
            attributeName="flood-opacity"
            values="0;1;0"
            dur="0.8s"
            repeatCount="indefinite"
          />
        </feDropShadow>
      </filter>
    </defs>
  </svg>
</template>

<style>
.bot-button-avatar {
  text-align: center !important;
  padding: 0 !important;
  width: 100%;
}

.audio-control-button {
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

  svg {
    width: 55px;
    padding: auto;
  }

  img {
    width: 90%;
  }
}

.audio-control-button:hover {
  box-shadow: 0px 0px 3px 3px rgba(45, 45, 45, 0.2);
  border-radius: 50%;
}

.silentAvatar {
}

.speakingAvatar {
  filter: url(#shadow);
}

.silentUser {
}

.speakingUser {
  filter: url(#shadow);
}
</style>
