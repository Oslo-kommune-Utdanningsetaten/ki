<script setup>
import BotAvatar from '@/components/BotAvatar.vue'
import { renderMessage } from '../utils/renderTools.js'

const props = defineProps({
  messages: Array,
  bot: Object,
})
</script>

<template>
  <div class="container border px-0 py-3">
    <div class="row g-0">
      <div class="col-md-1 d-flex align-items-center justify-content-center">
        <div class="avatar">
          <BotAvatar :avatar_scheme="props.bot.avatar_scheme" />
        </div>
      </div>
      <div class="col-md-10">
        <div
          v-for="(aMessage, messageIndex) in messages.slice(1, messages.length)"
          :key="messageIndex"
          class="mb-4 mt-0"
        >
          <div
            v-if="aMessage.role === 'user'"
            class="d-flex justify-content-end align-items-end text-end"
          >
            <div
              class="w-60 position-relative p-2 bubble bubble-user"
              v-html="renderMessage(aMessage.content)"
            ></div>
          </div>
          <div v-else class="d-flex justify-content-start align-items-start">
            <div
              class="w-60 position-relative bg-light p-2 bubble bubble-assistant"
              v-html="renderMessage(aMessage.content)"
            ></div>
          </div>
        </div>
      </div>
      <div class="col-md-1 d-flex align-items-center justify-content-center">
        <div class="avatar">
          <img alt="User Avatar" class="ms-2" src="@/components/icons/user.svg" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bubble-user {
  background-image: linear-gradient(to right, white, #b3f5ff);
}

.bubble-assistant {
  background-image: linear-gradient(to right, rgb(227, 227, 227), white);
}

.bubble p:last-child {
  margin-bottom: 0;
}
</style>
