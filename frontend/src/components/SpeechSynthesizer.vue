<script setup>
import { ref, onMounted } from 'vue'
const synth = window.speechSynthesis

const props = defineProps({
  textInput: String,
})
// Used to keep track of whether the play function should play from the beginning, or resume
const isResumeable = ref(false)
const isCurrentlyPlaying = ref(false)
const utterance = new SpeechSynthesisUtterance()

const configureSynthesizer = () => {
  if (synth) {
    utterance.voice = synth
      .getVoices()
      .find(aVoice => aVoice.lang === navigator.language || navigator.userLanguage)
    utterance.volume = 1
    utterance.rate = 0.9
    utterance.pitch = 1
    utterance.text = props.textInput
    utterance.lang = navigator.language || navigator.userLanguage
    // Set up event handlers
    utterance.onend = handleSpeechEnd
    utterance.onerror = handleSpeechError
  } else {
    console.warn('Speech synthesis not supported in this browser')
  }
}

const toggleSpeech = () => {
  if (isCurrentlyPlaying.value) {
    pause()
  } else {
    play()
  }
  isCurrentlyPlaying.value = !isCurrentlyPlaying.value
}

const play = () => {
  if (isResumeable.value) {
    synth.resume()
  } else {
    synth.cancel()
    synth.speak(utterance)
    isResumeable.value = true
  }
}

const pause = () => {
  synth.pause()
}

const handleSpeechEnd = () => {
  isCurrentlyPlaying.value = false
  isResumeable.value = false
}

const handleSpeechError = event => {
  console.error('Speech synthesis error:', event.error)
  isCurrentlyPlaying.value = false
  isResumeable.value = false
}

onMounted(() => {
  configureSynthesizer()
})
</script>

<template v-if="!!synth">
  <a name="toggleSpeech" @click="toggleSpeech">
    <img
      v-if="isCurrentlyPlaying"
      class="oslo-fill-dark-black"
      src="@/components/icons/pause.svg"
      alt="Pause avspilling"
      title="Pause avspilling"
    />
    <img
      v-else
      class="oslo-fill-dark-black"
      src="@/components/icons/play.svg"
      alt="Spill av denne meldingen"
      title="Spill av denne meldingen"
    />
  </a>
</template>
