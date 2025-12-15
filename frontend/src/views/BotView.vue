<script setup>
import { useRouter, useRoute } from 'vue-router'
import { ref, onMounted, computed, provide } from 'vue'
import { getBot } from '@/utils/httpTools.js'

const route = useRoute()
const router = useRouter()
const bot = ref()
const systemPrompt = ref('')
provide('bot', bot)
// provide('systemPrompt', systemPrompt)

onMounted(async () => {
  bot.value = await getBot(route.params.id)
  if (!bot.value) {
    router.push({ name: 'home' })
    return
  }
})
</script>

<template>
  <RouterView v-if="bot" />
</template>
