<script setup>
import { ref, nextTick, watch, onMounted, onBeforeUnmount } from 'vue'
import BotAvatar from '@/components/BotAvatar.vue'
import ConversationSimple from '@/components/ConversationSimple.vue'
import AudioWave from '@/components/AudioWave.vue'
import workletURL from '@/utils/pcm-processor.js?url'

import {
  languageOptions,
  getSelectedLanguage,
  getSelectedVoice,
  getVoicesForLanguage,
  updateLanguagePreferences,
} from '../utils/audioOptions.js'

const props = defineProps({
  bot: {
    type: Object,
    required: true,
  },
  systemPrompt: {
    type: String,
  },
})

// const websocketUrl = import.meta.env.DEV
//   ? 'ws://localhost:8000/ws/audio/'
//   : `wss://${window.location.host}/ws/audio/`

const websocketUrl = 'ws://iz-ki-ap01t.oslo.int/ws/audio/'

const isMicRecording = ref(false)
const isBotSpeaking = ref(false)
const isLanguageOptionsVisible = ref(false)
const isDebugHistoryVisible = ref(false)
const currentServerStatus = ref('')
const statusHistory = ref([])
const startTime = ref(null)
const messages = ref([])
const selectedLanguage = ref(getSelectedLanguage())
const selectedVoice = ref(getSelectedVoice(selectedLanguage.value))
const availableVoices = ref(getVoicesForLanguage(selectedLanguage.value))

let connectionRetries = 0
const maxConnectionRetries = 5

let microphonePermissionStatus = ref('denied')
let audioContext
let audioSource
let websocket

const elapsedSeconds = () => {
  if (!startTime.value) return 0
  return Math.floor((Date.now() - startTime.value) / 1000)
}

const handleToggleDebug = () => {
  isDebugHistoryVisible.value = !isDebugHistoryVisible.value
}

const setMic = position => {
  if (position === 'on') isMicRecording.value = true
  else if (position === 'off') isMicRecording.value = false
  recordEvent(`Mic: ${position}`)
}

const setBotSpeaking = position => {
  if (position === 'on') isBotSpeaking.value = true
  else if (position === 'off') isBotSpeaking.value = false
  recordEvent(`Bot speak: ${position}`)
}

const handleToggleRecording = async () => {
  // start and stop functions handle toggling of isMicRecording.value
  if (!isMicRecording.value) {
    await initializeWebsocket()
    await startRecording()
  } else {
    await stopRecording()
  }
}

const recordEvent = description => {
  statusHistory.value.push({ time: elapsedSeconds(), event: description })
}

const handleTogglePlayback = () => {
  recordEvent('handleTogglePlayback')
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

const initializeWebsocket = async () => {
  if (audioContext) {
    await audioContext.close()
  }
  audioContext = null

  const audioChunks = []

  try {
    websocket = new WebSocket(websocketUrl)
  } catch (error) {
    console.error('Error while creating WebSocket', error)
    return
  }

  websocket.onerror = error => {
    console.error('WebSocket error details:', {
      url: websocket.url,
      readyState: websocket.readyState,
      protocol: websocket.protocol,
      error: error,
    })
  }

  websocket.onopen = () => {
    recordEvent('WebSocket opened')

    sendServerConfig()

    // send initial messages
    websocket.send(
      JSON.stringify({
        type: 'websocket.text',
        messages: messages.value,
      })
    )
  }

  websocket.onclose = async event => {
    recordEvent(`WebSocket closed with code: ${event.code}. Reason: ${event.reason}`)
    setMic('off')
    setBotSpeaking('off')

    // 1000 is the normal close code, anything above that is an error
    if (event.code > 1000) {
      if (connectionRetries < maxConnectionRetries) {
        setTimeout(async () => {
          connectionRetries++
          recordEvent(
            `WebSocket closed unexpectedly, attempting reconnect ${connectionRetries} of ${maxConnectionRetries}`
          )
          await initializeWebsocket()
          await startRecording()
        }, 1000 * connectionRetries)
      } else {
        recordEvent('WebSocket closed unexpectedly, max retries reached')
        return
      }
    }
  }

  websocket.onmessage = event => {
    if (typeof event.data === 'string') {
      // server is updating messages or reporting on its status
      const { type, command, serverStatus, messages: updatedMessages } = JSON.parse(event.data)
      if (type === 'websocket.text' && updatedMessages) {
        messages.value = [...updatedMessages]
        scrollToPageBottom()
      }
      if (serverStatus) {
        currentServerStatus.value = serverStatus
        recordEvent(`Server status: ${serverStatus}`)
        if (
          [
            'sendingTextToClient',
            'generatingChatResponse',
            'generatingAudioResponse',
            'streamingAudioToClient',
          ].includes(serverStatus)
        ) {
          setMic('off')
        }
      }
      if (type === 'websocket.audio') {
        if (command === 'audio-stream-begin') {
          // turn off mic while bot is speaking
          setMic('off')
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
}

const startRecording = async () => {
  setMic('on')
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
    if (websocket && websocket.readyState === WebSocket.OPEN && isMicRecording.value) {
      websocket.send(pcmData)
    }
  }
}

const stopRecording = async () => {
  recordEvent('stopRecording')
  setMic('off')
  setBotSpeaking('off')
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
      setBotSpeaking('on')
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
  recordEvent('Audio playback finished')
  setBotSpeaking('off')
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    setMic('on')
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
        bot_model: props.bot.model?.deployment_id,
      })
    )
  }
}

const checkMicrophonePermissionStatus = async () => {
  const permission = await navigator.permissions.query({ name: 'microphone' })
  microphonePermissionStatus.value = permission.state
}

const scrollToPageBottom = () => {
  //window.scrollTo(0, document.body.scrollHeight || document.documentElement.scrollHeight)
  nextTick(() => {
    window.scrollTo({
      top: document.body.scrollHeight,
      left: 0,
      behavior: 'smooth',
    })
  })
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
  startTime.value = Date.now()
})

onBeforeUnmount(() => {
  websocket.close()
})
</script>

<template>
  <div class="border mb-3">
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
          class="audio-control me-4"
          :class="{
            'audio-control-button-stop': isBotSpeaking,
            'audio-control-button ': isBotSpeaking,
          }"
          :title="isBotSpeaking ? 'Trykk for å pause bablinga' : 'Stille som en mus'"
          :disabled="microphonePermissionStatus === 'denied' || !isBotSpeaking"
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
          <select v-model="selectedLanguage" class="form-select mb-3" @input="handleFormEdited">
            <option
              v-for="language in languageOptions.languages"
              :key="language.code"
              :value="language.code"
            >
              {{ language.name }}
            </option>
          </select>

          <label for="voice">Stemme</label>
          <select v-model="selectedVoice" class="form-select mb-3">
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
          class="audio-control audio-control-button"
          :class="{ 'audio-control-button-stop': isMicRecording }"
          :title="
            microphonePermissionStatus === 'denied'
              ? 'Nettleseren har ikke tilgang til mikrofonen'
              : isMicRecording
                ? 'Trykk for å stoppe innspilling'
                : 'Trykk for å snakke'
          "
          :disabled="microphonePermissionStatus === 'TMP_denied'"
        >
          <AudioWave v-if="isMicRecording" />
          <img v-else src="@/components/icons/microphone.svg" class="mic-icon" alt="mikrofon" />
        </button>
      </div>
    </div>
  </div>

  <div>
    <a @click="handleToggleDebug" class="invisible-button">
      {{ isDebugHistoryVisible ? 'Skjul' : 'Vis' }} debughistorikk
    </a>
    <table v-if="isDebugHistoryVisible" class="table table-sm table-striped">
      <thead>
        <tr>
          <th>Time</th>
          <th>Event</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="status in statusHistory">
          <td>{{ status.time }}</td>
          <td>{{ status.event }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style>
.invisible-button {
  color: transparent;
  background-color: transparent;
  border: none;
  cursor: pointer;
}

.audio-control {
  position: relative;
  pointer-events: auto;
  border-radius: 50%;
  border: none;
  height: 120px;
  width: 120px;
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

.audio-control-button {
  background-color: rgba(220, 220, 220, 0.5);
  transition: box-shadow 0.1s ease-in-out;
}

.audio-control-button:hover {
  box-shadow: 0px 0px 6px 4px rgba(45, 45, 45, 0.25);
}

.audio-control-button-stop:hover::after {
  content: '×'; /* asdf */
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
