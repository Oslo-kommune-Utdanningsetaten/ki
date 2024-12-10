<script setup>
import { ref, watch } from 'vue'
import AudioWave from '@/components/AudioWave.vue'
import workletURL from '../utils/pcm-processor.js?url'

const props = defineProps({
  readOutLoud: String,
  onTranscriptReceived: Function,
})

const websocketUrl = 'ws://localhost:5000/ws/audio/'
let audioContext
let websocket
const isRecording = ref(false)

const handleToggleRecording = () => {
  isRecording.value = !isRecording.value
  if (isRecording.value) {
    startRecording()
  } else {
    stopRecording()
  }
}

const startRecording = async () => {
  // Open WebSocket connection
  websocket = new WebSocket(websocketUrl)
  const audioChunks = []
  websocket.onmessage = event => {
    if (typeof event.data === 'string') {
      const { type, status, transcript } = JSON.parse(event.data)
      if (type === 'websocket.text' && transcript) {
        console.info('Received text', transcript)
        props.onTranscriptReceived(transcript)
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
        source.start(0)
      },
      error => {
        console.error('Error while decoding audio data', error)
      }
    )
  }

  websocket.onopen = () => {
    console.log('WebSocket connection opened')
  }

  websocket.onclose = () => {
    console.log('WebSocket connection closed')
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

  // When ever the workletNode is done processing a chunk if data from the input stream, pipe data to websocket
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

// Watch for changes in props.readOutLoud
watch(
  () => props.readOutLoud,
  (newReadOutLoud, oldReadOutLoud) => {
    if (newReadOutLoud && newReadOutLoud !== oldReadOutLoud) {
      websocket.send(JSON.stringify({ message: newReadOutLoud }))
    }
  }
)
</script>

<template>
  <div>
    <button @click="() => handleToggleRecording()">
      <AudioWave v-if="isRecording" />
      <span v-else>Start Recording</span>
    </button>
  </div>
</template>
