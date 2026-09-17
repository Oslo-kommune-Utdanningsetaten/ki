<script setup>
import { nextTick, watch } from 'vue'
import MessageBubble from '@/components/MessageBubble.vue'

const props = defineProps({
  messages: Array,
  isProcessingInput: Boolean,
  isStreaming: Boolean,
  bot: Object,
  handleEditMessageAtIndex: Function,
})

const scrollToBottom = () => {
  nextTick(() => {
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
  })
}

watch(() => props.messages, scrollToBottom, { deep: true })
</script>

<template>
  <div v-if="props.messages.length" class="card mt-3 p-3">
    <MessageBubble
      v-for="(aMessage, messageIndex) in props.messages"
      :key="messageIndex"
      :message="aMessage"
      :messageIndex="messageIndex"
      :isLast="messageIndex === props.messages.length - 1"
      :isProcessingInput="props.isProcessingInput"
      :bot="props.bot"
      :handleEditMessageAtIndex="props.handleEditMessageAtIndex"
    />
  </div>
</template>
