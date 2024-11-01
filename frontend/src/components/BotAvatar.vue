<script setup>
import { watchEffect } from 'vue'
import { createBotDescriptionFromScheme } from '../utils.js'
import BotAvatarSvgBodyPart from '@/components/BotAvatarSvgBodyPart.vue'

const attr = defineProps(['avatar_scheme'])

let bot

watchEffect(() => {
  bot = createBotDescriptionFromScheme(attr.avatar_scheme)
})
</script>

<template>
  <!-- Is used to trigger the watchEffect() function -->
  <div hidden>
    {{ attr.avatar_scheme }}
  </div>

  <!-- Body parts could have been drawn by iterating over bot key/values, but order (z-index) is important -->
  <svg viewBox="0 0 12 18">
    <!-- neck -->
    <BotAvatarSvgBodyPart :body_part="bot.neck" />

    <!-- head -->
    <BotAvatarSvgBodyPart :body_part="bot.head" />

    <!-- ears -->
    <BotAvatarSvgBodyPart :body_part="bot.ears" />

    <!-- body -->
    <BotAvatarSvgBodyPart :body_part="bot.body" />

    <!-- eyes -->
    <BotAvatarSvgBodyPart :body_part="bot.eyes" />

    <!-- arms -->
    <BotAvatarSvgBodyPart :body_part="bot.arms" />

    <!-- hair -->
    <BotAvatarSvgBodyPart :body_part="bot.hair" />
  </svg>
</template>
