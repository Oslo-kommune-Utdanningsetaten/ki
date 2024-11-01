<script setup>
// Draws a single body part of the bot avatar

import { watchEffect } from 'vue'
const attr = defineProps(['body_part'])
let bodyPart = attr.body_part

watchEffect(() => {
  bodyPart = attr.body_part
})
</script>

<template>
  <g v-for="shape in bodyPart.shapes">
    <polygon v-if="shape.type === 'polygon'" :class="shape.color" :points="shape.points" />
    <circle
      v-else-if="shape.type === 'circle'"
      :class="shape.color"
      :cx="shape.cx"
      :cy="shape.cy"
      :r="shape.r"
    />
    <rect
      v-else
      :class="shape.color"
      :x="shape.x"
      :y="shape.y"
      :width="shape.width"
      :height="shape.height"
    />
  </g>
</template>
