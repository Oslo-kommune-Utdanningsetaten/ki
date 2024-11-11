<script setup>
// Draws a single body part of the bot avatar

const props = defineProps({
  bodyPart: Object,
})
</script>

<template v-if="props.bodyPart">
  <g v-for="shape in props.bodyPart.shapes">
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
