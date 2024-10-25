<script setup>
import { watchEffect, watch } from 'vue'

const attr = defineProps(['image_attr'])

let color = []
let highHead = false
let ears = false
let arms = false
let thinNeck = false
let hair = 0
let eyes = 0
let eyesYpos = 4
const colors = [
  ['oslo-fill-blue', 'oslo-fill-dark-blue'],
  ['oslo-fill-yellow', 'oslo-fill-black'],
  ['oslo-fill-green', 'oslo-fill-dark-green'],
  ['oslo-fill-red', 'oslo-fill-black'],
  ['oslo-fill-dark-beige', 'oslo-fill-black'],
]

watchEffect(() => {
  color = colors[0]
  console.log(attr.image_attr)
  try {
    for (const [key, value] of attr.image_attr.entries()) {
      if (key === 0) {
        color = colors[value]
      } else if (key === 1) {
        highHead = value == 1 ? true : false
        eyesYpos = highHead ? 1 : 3
      } else if (key === 2) {
        eyes = value
      } else if (key === 3) {
        hair = value
      } else if (key === 4) {
        ears = value == 1 ? true : false
      } else if (key === 5) {
        arms = value == 1 ? true : false
      } else if (key === 6) {
        thinNeck = value == 1 ? true : false
      }
    }
  } catch (error) {
    console.log(error)
  }
})
</script>

<template>
  <!-- Is used to trigger the watchEffect() function -->
  <div hidden>
    {{ attr.image_attr }}
  </div>

  <svg viewBox="0 0 12 18">
    <!-- neck -->
    <rect v-if="thinNeck" :class="color[1]" x="5" y="4" width="2" height="6" />
    <rect v-else :class="color[1]" x="4" y="4" width="4" height="6" />
    <!-- head -->
    <rect v-if="highHead" :class="color[0]" x="2" width="8" height="4" />
    <rect v-else :class="color[0]" x="2" width="8" height="8" />
    <!-- ears -->
    <rect v-if="ears" :class="color[1]" x="1" :y="eyesYpos" width="1" height="2" />
    <rect v-if="ears" :class="color[1]" x="10" :y="eyesYpos" width="1" height="2" />
    <!-- body -->
    <rect :class="color[0]" x="2" y="10" width="8" height="8" />
    <!-- eyes -->
    <circle v-if="eyes == 0" :class="color[1]" cx="4" :cy="eyesYpos + 1" r="1" />
    <circle v-if="eyes == 0" :class="color[1]" cx="8" :cy="eyesYpos + 1" r="1" />
    <rect v-if="[1, 3].includes(eyes)" :class="color[1]" x="3" :y="eyesYpos" width="2" height="2" />
    <rect v-if="eyes == 1" :class="color[1]" x="7" :y="eyesYpos" width="2" height="2" />
    <rect v-if="eyes == 2" :class="color[1]" x="3" :y="eyesYpos" width="2" height="1" />
    <rect v-if="[2, 3].includes(eyes)" :class="color[1]" x="7" :y="eyesYpos" width="2" height="1" />
    <!-- arms -->
    <rect v-if="arms" :class="color[1]" x="2" y="10" width="2" height="6" />
    <polygon v-else :class="color[1]" points="0 10 0 14 2 14 2 12 4 12 4 10 0 10" />
    <rect v-if="arms" :class="color[1]" x="8" y="10" width="2" height="6" />
    <polygon v-else :class="color[1]" points="8 10 8 12 10 12 10 14 12 14 12 10 8 10" />
    <!-- hair -->
    <rect v-if="hair == 1 && !highHead" :class="color[1]" x="2" y="0" width="8" height="2" />
    <polygon
      v-if="hair == 2 && !highHead"
      :class="color[1]"
      points="2 0 10 0 10 2 9 2 9 1 8 1 8 2 6 2 6 1 5 1 5 2 4 2 4 1 3 1 3 2 2 2 2 0"
    />
  </svg>
</template>
