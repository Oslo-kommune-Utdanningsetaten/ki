<script setup>
import { watchEffect } from 'vue'
import { createBotDescriptionFromScheme } from '../utils.js'

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

  <svg viewBox="0 0 12 18">
    <!-- neck -->
    <g v-for="neck in bot.neck.shapes">
      <rect :class="neck.color" :x="neck.x" :y="neck.y" :width="neck.width" :height="neck.height" />
    </g>

    <!-- head -->
    <g v-for="head in bot.head.shapes">
      <rect :class="head.color" :x="head.x" :width="head.width" :height="head.height" />
    </g>

    <!-- ears -->
    <g v-for="ear in bot.ears.shapes">
      <rect :class="ear.color" :x="ear.x" :y="ear.y" :width="ear.width" :height="ear.height" />
    </g>

    <!-- body -->
    <g v-for="body in bot.body.shapes">
      <rect :class="body.color" :x="body.x" :y="body.y" :width="body.width" :height="body.height" />
    </g>

    <!-- eyes -->
    <g v-for="eye in bot.eyes.shapes">
      <circle
        v-if="eye.type === 'circle'"
        :class="eye.color"
        :cx="eye.cx"
        :cy="eye.cy"
        :r="eye.r"
      />
      <rect
        v-else
        :class="eye.color"
        :x="eye.x"
        :y="eye.y"
        :width="eye.width"
        :height="eye.height"
      />
    </g>

    <!-- arms -->
    <g v-for="arm in bot.arms.shapes">
      <polygon v-if="arm.type === 'polygon'" :class="arm.color" :points="arm.points" />
      <rect
        v-else
        :class="arm.color"
        :x="arm.x"
        :y="arm.y"
        :width="arm.width"
        :height="arm.height"
      />
    </g>

    <!-- hair -->
    <g v-for="hair in bot.hair.shapes">
      <polygon v-if="hair.type === 'polygon'" :class="hair.color" :points="hair.points" />
      <rect
        v-else
        :class="hair.color"
        :x="hair.x"
        :y="hair.y"
        :width="hair.width"
        :height="hair.height"
      />
    </g>
  </svg>
</template>
