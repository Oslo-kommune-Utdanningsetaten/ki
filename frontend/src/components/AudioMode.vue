<script setup>
import { ref } from 'vue'
import AudioWave from '@/components/AudioWave.vue'
import workletURL from '../utils/pcm-processor.js?url'

const props = defineProps({
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
  websocket.onmessage = event => {
    const { transcript } = JSON.parse(event.data)
    console.info('transcript', transcript)
    if (transcript) {
      props.onTranscriptReceived(transcript)
    }
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
    } else {
      console.info('Expected open WebSocket on', websocketUrl)
    }
  }

  // Connect the audioSourceNode to the worklet for processing
  audioSourceNode.connect(workletNode)

  console.log('Recording started...')
}

const stopRecording = () => {
  if (audioContext) {
    audioContext.close()
  }
  if (websocket) {
    websocket.close()
  }
  console.log('Recording stopped.')
}
</script>

<template>
  <div>
    <button @click="() => handleToggleRecording()">
      <AudioWave v-if="isRecording" />
      <span v-else>Start Recording</span>
    </button>
  </div>
</template>
