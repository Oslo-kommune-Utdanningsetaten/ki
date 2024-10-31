<script setup>
import { watchEffect } from 'vue'
import { createBotDescriptionFromScheme } from '../utils.js'

const attr = defineProps(['avatar_scheme'])

// Maybe move this to createBotDescriptionFromScheme?
const colors = [
  ['oslo-fill-blue', 'oslo-fill-dark-blue'],
  ['oslo-fill-yellow', 'oslo-fill-black'],
  ['oslo-fill-green', 'oslo-fill-dark-green'],
  ['oslo-fill-red', 'oslo-fill-black'],
  ['oslo-fill-dark-beige', 'oslo-fill-black'],
]

let bot

watchEffect(() => {
  bot = createBotDescriptionFromScheme(attr.avatar_scheme)
})
</script>

<template>
  <!-- Is used to trigger the watchEffect() function -->
  <div hidden>
    {{ attr.avatar_scheme }}
    <pre>{{ JSON.stringify(bot, null, 2) }}</pre>
  </div>

  <svg viewBox="0 0 12 18">
    <!-- neck -->
    <span v-for="neck in bot.neck.shapes">
      <rect
        :class="bot.colors[1]"
        :x="neck.x"
        :y="neck.y"
        :width="neck.width"
        :height="neck.height"
      />
    </span>

    <!-- head -->
    <span v-for="head in bot.head.shapes">
      <rect :class="bot.colors[0]" :x="head.x" :width="head.width" :height="head.height" />
    </span>

    <!-- ears -->
    <span v-for="ear in bot.ears.shapes">
      <rect :class="bot.colors[1]" :x="ear.x" :y="ear.y" :width="ear.width" :height="ear.height" />
    </span>

    <!-- body -->
    <span v-for="body in bot.body.shapes">
      <rect
        :class="bot.colors[0]"
        :x="body.x"
        :y="body.y"
        :width="body.width"
        :height="body.height"
      />
    </span>

    <!-- eyes -->
    <span v-for="eye in bot.eyes.shapes">
      <circle
        v-if="eye.type === 'circle'"
        :class="bot.colors[1]"
        :cx="eye.cx"
        :cy="eye.cy"
        :r="eye.r"
      />
      <rect
        v-else
        :class="bot.colors[1]"
        :x="eye.x"
        :y="eye.y"
        :width="eye.width"
        :height="eye.height"
      />
    </span>

    <!-- arms -->
    <span v-for="arm in bot.arms.shapes">
      <polygon v-if="arm.type === 'polygon'" :class="bot.colors[1]" :points="arm.points" />
      <rect
        v-else
        :class="bot.colors[1]"
        :x="arm.x"
        :y="arm.y"
        :width="arm.width"
        :height="arm.height"
      />
    </span>

    <!-- hair -->
    <span v-for="hair in bot.hair.shapes">
      <polygon v-if="hair.type === 'polygon'" :class="bot.colors[1]" :points="hair.points" />
      <rect
        v-else
        :class="bot.colors[1]"
        :x="hair.x"
        :y="hair.y"
        :width="hair.width"
        :height="hair.height"
      />
    </span>
  </svg>
</template>
