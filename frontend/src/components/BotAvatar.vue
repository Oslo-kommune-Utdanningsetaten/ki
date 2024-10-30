<script setup>
import { watchEffect } from 'vue'
import { createBotDescriptionFromScheme } from '../utils.js'

const attr = defineProps(['avatar_scheme'])
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
  </div>

  <svg viewBox="0 0 12 18">
    <!-- neck -->
    <rect
      :class="bot.colors[1]"
      :x="bot.neck.x"
      :y="bot.neck.y"
      :width="bot.neck.width"
      :height="bot.neck.height"
    />

    <!-- head -->
    <rect :class="color[0]" :x="bot.head.x" :width="bot.head.width" :height="bot.head.height" />

    <!-- ears -->
    <span v-for="ear in bot.ears.shapes">
      <rect :class="color[1]" :x="ear.x" :y="ear.y" :width="ear.width" :height="ear.height" />
    </span>

    <!-- body -->
    <rect
      :class="color[0]"
      :x="bot.body.x"
      :y="bot.body.y"
      :width="bot.body.width"
      :height="bot.body.height"
    />

    <!-- eyes -->
    <span v-for="eye in bot.eyes.shapes">
      <circle v-if="eye.type === 'circle'" :class="color[1]" :cx="eye.cx" :cy="eye.cy" :r="eye.r" />
      <rect
        v-else
        :class="color[1]"
        :x="eye.x"
        :y="eye.y"
        :width="eye.width"
        :height="eye.height"
      />
    </span>

    <!-- arms -->
    <span v-for="arm in bot.arms.shapes">
      <polygon v-if="arm.type === 'polygon'" :class="color[1]" :points="arm.points" />
      <rect
        v-else
        :class="color[1]"
        :x="arm.x"
        :y="arm.y"
        :width="arm.width"
        :height="arm.height"
      />
    </span>

    <!-- hair -->
    <rect
      v-if="bot.hair.description === 'flat'"
      :class="color[1]"
      :x="bot.hair.x"
      :y="bot.hair.y"
      :width="bot.hair.width"
      :height="bot.hair.height"
    />
    <polygon
      v-else-if="bot.hair.description === 'scruffy'"
      :class="color[1]"
      :points="bot.hair.points"
    />
  </svg>
</template>
