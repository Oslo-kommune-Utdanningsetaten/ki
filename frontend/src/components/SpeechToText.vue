<script setup>
import { ref, onMounted } from 'vue'
import AudioWave from '@/components/AudioWave.vue'

const props = defineProps({
  onMessageReceived: Function,
})

// Does the browser support speech recognition
const isBrowserSpeechEnabled = ref(false)
// Has the user granted permission to use the microphone
let microphonePermissionStatus = ref('denied')
// Are we currently listening for speech input
const isSpeechRecognitionActive = ref(false)
// Speech recognition session
let speechRecognitionSession

const initializeSpeechRecognition = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

  if (SpeechRecognition) {
    let speechTranscript = null
    isBrowserSpeechEnabled.value = true

    speechRecognitionSession = new SpeechRecognition()
    speechRecognitionSession.lang = navigator.language || navigator.userLanguage
    speechRecognitionSession.interimResults = false
    speechRecognitionSession.maxAlternatives = 1

    // Set up event handlers
    speechRecognitionSession.onstart = () => {
      isSpeechRecognitionActive.value = true
    }

    speechRecognitionSession.onresult = event => {
      const transcript = event.results[0][0].transcript
      speechTranscript = transcript
      isSpeechRecognitionActive.value = false
    }

    speechRecognitionSession.onerror = event => {
      console.error('Speech recognition error:', event.error)
      isSpeechRecognitionActive.value = false
    }

    speechRecognitionSession.onend = () => {
      isSpeechRecognitionActive.value = false
      if (speechTranscript) {
        // Speech is assumend finished
        props.onMessageReceived(speechTranscript)
      } // TODO: maybe show a heads-up to the user that recognition ended but no transcript was received
    }
  } else {
    isBrowserSpeechEnabled.value = false
  }
}

const checkMicrophonePermissionStatus = async () => {
  const permission = await navigator.permissions.query({ name: 'microphone' })
  microphonePermissionStatus.value = permission.state
}

const toggleSpeechInput = () => {
  // Fail early if speech recognition has not been set up
  if (!speechRecognitionSession) return
  if (isSpeechRecognitionActive.value) {
    speechRecognitionSession.stop()
  } else {
    initializeSpeechRecognition()
    speechRecognitionSession.start()
  }
}

onMounted(() => {
  checkMicrophonePermissionStatus()
  initializeSpeechRecognition()
})
</script>

<template>
  <button
    v-if="isBrowserSpeechEnabled"
    @click="toggleSpeechInput"
    class="btn oslo-btn-secondary mic-button ms-0"
    :title="
      microphonePermissionStatus === 'denied'
        ? 'Nettleseren har ikke tilgang til mikrofonen'
        : 'Trykk for å snakke inn tekst'
    "
    :disabled="microphonePermissionStatus === 'denied' || isSpeechRecognitionActive"
  >
    <AudioWave v-if="isSpeechRecognitionActive" />
    <img v-else src="@/components/icons/microphone.svg" class="mic-icon" alt="mikrofon" />
  </button>
</template>

<style scoped>
.mic-button {
  pointer-events: auto;
}

.mic-icon {
  transform: scale(1.2);
  display: inline-block;
  transition: transform 0.2s ease-out;
}

.mic-button:hover .mic-icon {
  transform: scale(1.5);
}
</style>
s
