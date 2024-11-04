<script setup>
import { ref, onMounted } from 'vue'
const synth = window.speechSynthesis

const isResumeable = ref(false) // use this to keep track of whether the start function should play or resume
const isCurrentlyPlaying = ref(false)
const utterance = new SpeechSynthesisUtterance()

// the text to be spoken
const attr = defineProps(['textInput'])
let textInput = ref(attr.textInput)

const configureSynthesizer = () => {
  if (synth) {
    utterance.voice = synth
      .getVoices()
      .find(aVoice => aVoice.lang === navigator.language || navigator.userLanguage)
    utterance.volume = 1
    utterance.rate = 0.9
    utterance.pitch = 1
    utterance.text = textInput.value
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

<template>
  <a href="#" @click="toggleSpeech">
    <img v-if="isCurrentlyPlaying" src="@/components/icons/pause.svg" alt="Pause avspilling" />
    <img v-else src="@/components/icons/play.svg" alt="Spill av denne meldingen" />
  </a>
</template>
