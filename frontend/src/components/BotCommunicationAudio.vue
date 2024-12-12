<script setup>
import { ref } from 'vue'

import AudioMode from '@/components/AudioMode.vue'

const messages = ref([])
const lastBotMessage = ref('')

const props = defineProps({
  bot: {
    type: Object,
    required: true,
  },
  systemPrompt: {
    type: String,
  },
})

const handleTranscriptReceived = transcript => {
  console.log('Transcript received:', transcript)
}
</script>

<template>
  <AudioMode :readOutLoud="lastBotMessage" :onTranscriptReceived="handleTranscriptReceived" />

  <pre>{{ JSON.stringify(messages.value, null, 2) }}</pre>
</template>
