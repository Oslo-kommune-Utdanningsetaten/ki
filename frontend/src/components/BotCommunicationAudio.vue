<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
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

// serverStatus is one of: 'websocketOpened', 'websocketClosed','initializing', 'streamingAudioToAzure', 'streamingTextToClient', 'generatingChatResponse', 'generatingAudioResponse', 'streamingAudioToClient', 'ready'

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
const isSpeechRecognitionActive = ref(false)
const isBotSpeaking = ref(false)
const serverStatusHistory = ref([])
const currentServerStatus = ref('')
const messages = ref([])
const selectedLanguage = ref(getSelectedLanguage())
const selectedVoice = ref(getSelectedVoice(selectedLanguage.value))
const availableVoices = ref(getVoicesForLanguage(selectedLanguage.value))
const statusChanged = ref(false)
let microphonePermissionStatus = ref('denied')

let audioContext
let audioSource
let websocket

const handleToggleRecording = () => {
  isSpeechRecognitionActive.value = !isSpeechRecognitionActive.value
  if (isSpeechRecognitionActive.value) {
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
    //isSpeechRecognitionActive.value = true
  }
}

const resetConversation = () => {
  messages.value = [
    {
      role: 'system',
      content: props.systemPrompt,
    },
  ]
}

const startRecording = async () => {
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

  // When workletNode is done processing a data chunk from the input stream, pipe data to websocket
  workletNode.port.onmessage = event => {
    const pcmData = event.data // This should now be PCM data, 16kHz, 16bit, mono
    if (websocket.readyState === WebSocket.OPEN && isSpeechRecognitionActive.value) {
      console.info('Send audio data to server', pcmData.byteLength)
      websocket.send(pcmData)
    }
  }
}

const initializeWebsocket = async () => {
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

  websocket.onmessage = event => {
    if (typeof event.data === 'string') {
      const { type, command, serverStatus, messages: updatedMessages } = JSON.parse(event.data)
      if (type === 'websocket.text' && updatedMessages) {
        messages.value = [...updatedMessages]
      }
      if (serverStatus) {
        console.info('Server status:', serverStatus)
        serverStatusHistory.value.push(serverStatus)
        currentServerStatus.value = serverStatus
        statusChanged.value = true
        setTimeout(() => {
          statusChanged.value = false
        }, 1000) // duration of the flash
      }
      if (type === 'websocket.audio') {
        if (command === 'audio-stream-begin') {
          //isSpeechRecognitionActive.value = false
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

  websocket.onclose = () => {
    console.info('webcocket closed')
    isBotSpeaking.value = false
    isSpeechRecognitionActive.value = false
  }
}

const stopRecording = () => {
  console.info('stopRecording')
  isSpeechRecognitionActive.value = false
}

const playAudioResponse = async audioChunks => {
  if (audioChunks.length === 0) {
    return
  }

  // Create a Blob with the correct MIME type
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
  isSpeechRecognitionActive.value = true
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

onMounted(() => {
  resetConversation()
  checkMicrophonePermissionStatus()
  initializeWebsocket()
})

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

onBeforeUnmount(() => {
  websocket.close()
})
</script>

<template>
  <div class="border p-3 mb-3">
    <span class="me-3">
      <label for="language">Velg språk:</label>
      <select v-model="selectedLanguage">
        <option
          v-for="language in languageOptions.languages"
          :key="language.code"
          :value="language.code"
        >
          {{ language.name }}
        </option>
      </select>
    </span>

    <span>
      <label for="voice">Velg stemme:</label>
      <select v-model="selectedVoice">
        <option v-for="voice in availableVoices" :key="voice.code" :value="voice.code">
          {{ voice.name }}
        </option>
      </select>
    </span>

    <h4 class="border p-3 mt-3">
      Server status:
      <span :class="{ glow: statusChanged }">{{ currentServerStatus }}</span>
    </h4>
    <div class="border p-3 mt-3">
      <!-- Avatar playback state and control -->
      <button
        @click="handleTogglePlayback"
        class="audio-control-button me-4"
        :class="isBotSpeaking ? 'speakingAvatar' : 'silentAvatar'"
        :title="isBotSpeaking ? 'Trykk for å pause bablinga' : 'Stille som en mus'"
        :disabled="microphonePermissionStatus === 'denied'"
      >
        <div class="svatar">
          <BotAvatar :avatar_scheme="props.bot.avatar_scheme" />
        </div>
      </button>

      <!-- User record state and control -->
      <button
        @click="handleToggleRecording"
        class="audio-control-button"
        :class="isSpeechRecognitionActive ? 'speakingUser' : 'silentUser'"
        :title="
          microphonePermissionStatus === 'denied'
            ? 'Nettleseren har ikke tilgang til mikrofonen'
            : isSpeechRecognitionActive
              ? 'Trykk for å stoppe innspilling'
              : 'Trykk for å snakke'
        "
        :disabled="microphonePermissionStatus === 'denied'"
      >
        <img src="@/components/icons/microphone.svg" class="mic-icon" alt="mikrofon" />
      </button>
    </div>
  </div>

  <ConversationSimple :messages="messages" :bot="props.bot" />

  <div class="border p-3 mt-3">
    <pre>
isSpeechRecognitionActive: {{ isSpeechRecognitionActive }}
isBotSpeaking: {{ isBotSpeaking }}
serverStatusHistory: {{ serverStatusHistory }}</pre
    >
  </div>

  <div class="border p-3 mt-3">
    <pre>{{ messages }}</pre>
  </div>

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
.audio-control-button {
  pointer-events: auto;
  height: 100px;
  width: 100px;
  background-color: transparent;
  box-sizing: border-box;
  border: none;

  svg {
    height: 82px;
  }

  img {
    width: 90%;
    transition: transform 0.2s ease-out;
  }
  img:hover {
    transform: scale(1.2);
  }
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

.glow {
  animation: glowEffect 1s ease-out;
}

@keyframes glowEffect {
  from {
    text-shadow:
      1px 1px 5px #e4aa2e,
      1px 1px 5px #c22323;
  }
  to {
    text-shadow: transparent;
  }
}
</style>
