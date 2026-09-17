<script setup>
import { ref, watch, onMounted } from 'vue'

const props = defineProps({ textInput: String })

const synth = window.speechSynthesis
const isCurrentlyPlaying = ref(false)
const isResumeable = ref(false)
const utterance = ref(new SpeechSynthesisUtterance())

const configureSynthesizer = () => {
  if (!synth) {
    console.warn('Speech synthesis not supported in this browser')
    return
  }

  const voices = synth.getVoices()
  utterance.value.voice = voices.find(
    aVoice => aVoice.lang === navigator.language || navigator.userLanguage
  )
  utterance.value.volume = 1
  utterance.value.rate = 0.9
  utterance.value.pitch = 1
  utterance.value.text = props.textInput
  utterance.value.lang = navigator.language || navigator.userLanguage

  utterance.value.onend = handleSpeechEnd
  utterance.value.onerror = handleSpeechError
}

const play = () => {
  if (!synth) return

  if (isResumeable.value && synth.paused) {
    synth.resume()
  } else {
    synth.cancel()
    synth.speak(utterance.value)
    isResumeable.value = true
  }
}

const pause = () => {
  if (synth) {
    synth.pause()
  }
}

const toggleSpeech = () => {
  if (isCurrentlyPlaying.value) {
    pause()
    isCurrentlyPlaying.value = false
  } else {
    play()
    isCurrentlyPlaying.value = true
  }
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

watch(
  () => props.textInput,
  () => {
    isCurrentlyPlaying.value = false
    isResumeable.value = false
    configureSynthesizer()
  }
)

onMounted(() => {
  configureSynthesizer()
})
</script>

<template v-if="!!synth">
  <a name="toggleSpeech" @click="toggleSpeech">
    <img
      v-if="isCurrentlyPlaying"
      class="oslo-fill-black"
      src="@/components/icons/pause.svg"
      alt="Pause avspilling"
      title="Pause avspilling"
    />
    <img
      v-else
      class="oslo-fill-black"
      src="@/components/icons/play.svg"
      alt="Spill av denne meldingen"
      title="Spill av denne meldingen"
    />
  </a>
</template>
