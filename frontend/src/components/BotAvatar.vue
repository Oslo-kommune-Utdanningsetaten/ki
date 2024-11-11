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
    <BotAvatarSvgBodyPart :bodyPart="bot.neck" />

    <!-- head -->
    <BotAvatarSvgBodyPart :bodyPart="bot.head" />

    <!-- ears -->
    <BotAvatarSvgBodyPart :bodyPart="bot.ears" />

    <!-- body -->
    <BotAvatarSvgBodyPart :bodyPart="bot.body" />

    <!-- eyes -->
    <BotAvatarSvgBodyPart :bodyPart="bot.eyes" />

    <!-- arms -->
    <BotAvatarSvgBodyPart :bodyPart="bot.arms" />

    <!-- hair -->
    <BotAvatarSvgBodyPart :bodyPart="bot.hair" />
  </svg>
</template>
