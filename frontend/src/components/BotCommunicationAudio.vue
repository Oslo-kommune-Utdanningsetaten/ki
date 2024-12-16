<script setup>
import { ref, watch, onMounted } from 'vue'
import AudioWave from '@/components/AudioWave.vue'
import BotAvatar from '@/components/BotAvatar.vue'

import workletURL from '../utils/pcm-processor.js?url'
import { renderMessage } from '../utils/renderTools.js'

const props = defineProps({
  bot: {
    type: Object,
    required: true,
  },
  systemPrompt: {
    type: String,
  },
})

// states
// user.isSendingAudio
// assistant.isSpeaking

const websocketUrl = 'ws://localhost:5000/ws/audio/'
const isRecording = ref(false)
const isBotSpeaking = ref(false)
const messages = ref([])
let audioContext
let websocket

const handleToggleRecording = () => {
  isRecording.value = !isRecording.value
  if (isRecording.value) {
    startRecording()
  } else {
    stopRecording()
  }
}

const onMessagesReceived = updatedMessages => {
  messages.value = [...updatedMessages]
}

const resetMessages = () => {
  messages.value = [
    {
      role: 'system',
      content: props.systemPrompt,
    },
  ]
}

const onAudioPlaybackFinished = () => {
  console.info('Audio playback finished')
  isBotSpeaking.value = false
}

const startRecording = async () => {
  // Open WebSocket connection
  websocket = new WebSocket(websocketUrl)
  websocket.onopen = () => {
    console.time('WebSocket', props.bot.uuid, messages.value)
    const textFrame = JSON.stringify({
      type: 'websocket.text',
      bot_uuid: props.bot.uuid,
      messages: messages.value,
    })
    websocket.send(textFrame)
  }

  const audioChunks = []
  websocket.onmessage = event => {
    if (typeof event.data === 'string') {
      const { type, status, messages: updatedMessages } = JSON.parse(event.data)
      if (type === 'websocket.text' && updatedMessages) {
        console.info('Received updatedMessages', updatedMessages)
        onMessagesReceived(updatedMessages)
      }
      if (type === 'websocket.audio') {
        if (status === 'start') {
          console.info('Received START')
          // start of audio stream, clear any lingering audio data
          audioChunks.length = 0
        } else if (status === 'stop') {
          console.info('Received STOP')
          playAudioResponse(audioChunks)
        }
      }
    } else {
      // received audio data, store it for later playback
      audioChunks.push(event.data)
    }
  }

  const playAudioResponse = async audioChunks => {
    if (audioChunks.length === 0) {
      console.warn('audioChunks is empty')
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
        const source = audioContext.createBufferSource()
        source.buffer = audioBuffer
        source.connect(audioContext.destination)
        isBotSpeaking.value = true
        source.start(0)
        source.onended = onAudioPlaybackFinished
      },
      error => {
        console.error('Error while decoding audio data', error)
      }
    )
  }

  websocket.onclose = () => {
    isRecording.value = false
    console.timeEnd('WebSocket')
  }

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

  // When workletNode is done processing a data chunk from the input stream, pipe data to websocket
  workletNode.port.onmessage = event => {
    const pcmData = event.data // This should now be PCM data, 16kHz, 16bit, mono
    if (websocket.readyState === WebSocket.OPEN) {
      websocket.send(pcmData)
    }
  }

  // Connect the audioSourceNode to the worklet for processing
  audioSourceNode.connect(workletNode)
}

const stopRecording = () => {
  if (websocket) {
    websocket.close()
  }
  if (audioContext) {
    audioContext.close()
  }
}

onMounted(() => {
  resetMessages()
})
</script>

<template>
  <div class="border p-3 mb-3">
    <button @click="() => handleToggleRecording()">
      <AudioWave v-if="isRecording" />
      <span v-else>Start Recording</span>
    </button>
    <pre>

isRecording: {{ isRecording }}
isBotSpeaking: {{ isBotSpeaking }}</pre
    >
  </div>

  <div class="container border px-0 py-3">
    <div class="row g-0">
      <div class="col-md-1 d-flex align-items-center justify-content-center">
        <div class="avatar">
          <BotAvatar :avatar_scheme="props.bot.avatar_scheme" />
        </div>
      </div>
      <div class="col-md-10">
        <div
          v-for="(aMessage, messageIndex) in messages.slice(1, messages.length)"
          :key="messageIndex"
          class="mb-4 mt-0"
        >
          <div
            v-if="aMessage.role === 'user'"
            class="d-flex justify-content-end align-items-end text-end"
          >
            <div
              class="w-60 position-relative p-2 bubble bubble-user"
              v-html="renderMessage(aMessage.content)"
            ></div>
          </div>
          <div v-else class="d-flex justify-content-start align-items-start">
            <div
              class="w-60 position-relative bg-light p-2 bubble bubble-assistant"
              v-html="renderMessage(aMessage.content)"
            ></div>
          </div>
        </div>
      </div>
      <div class="col-md-1 d-flex align-items-center justify-content-center">
        <div class="avatar">
          <img alt="User Avatar" class="ms-2" src="@/components/icons/user.svg" />
        </div>
      </div>
    </div>
  </div>

  <div class="border p-3 mt-3">
    <pre>{{ messages }}</pre>
  </div>
</template>

<style>
.bubble-user {
  background-image: linear-gradient(to right, white, #b3f5ff);
}

.bubble-assistant {
  background-image: linear-gradient(to right, rgb(248, 249, 250), white);
}

.bubble p:last-child {
  margin-bottom: 0;
}
</style>
