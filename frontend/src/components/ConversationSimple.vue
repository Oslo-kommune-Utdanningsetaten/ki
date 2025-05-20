<script setup>
import { ref } from 'vue'

import BotAvatar from '@/components/BotAvatar.vue'
import { renderMessage } from '../utils/renderTools.js'

const props = defineProps({
  messages: Array,
  bot: Object,
  onToggleReplay: Function,
  isCurrentlyPlaying: Boolean,
})

const handleToggleReplay = messageIndex => {
  // Add one to the index to account for the first message being sliced out
  props.onToggleReplay(messageIndex + 1)
}
</script>

<template>
  <div class="container px-0 py-3">
    <div class="row g-0">
      <div class="col-md-1 d-flex align-items-end justify-content-center">
        <div class="simple-conversation-avatar">
          <BotAvatar :avatarScheme="props.bot.avatarScheme" />
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
              class="w-60 position-relative p-2 bubble bubble-user speech-bubble-user"
              v-html="renderMessage(aMessage.content)"
            ></div>
          </div>
          <div
            v-else
            class="d-flex justify-content-start align-items-start position-relative message-container"
          >
            <div
              class="w-60 position-relative bg-light p-2 bubble bubble-assistant speech-bubble-assistant"
              v-html="renderMessage(aMessage.content)"
            ></div>

            <a
              name="toggleReplay"
              @click="() => handleToggleReplay(messageIndex)"
              class="position-absolute replay-widget"
            >
              <img
                v-if="props.isCurrentlyPlaying"
                class="oslo-fill-dark-black replay-icon"
                src="@/components/icons/pause.svg"
                alt="Pause avspilling"
                title="Pause avspilling"
              />
              <img
                v-else
                class="oslo-fill-dark-black replay-icon"
                src="@/components/icons/play.svg"
                alt="Spill av på nytt"
                title="Spill av på nytt"
              />
            </a>
          </div>
        </div>
      </div>
      <div class="col-md-1 d-flex align-items-end justify-content-center">
        <div class="simple-conversation-avatar">
          <img alt="User Avatar" class="ms-2" src="@/components/icons/user.svg" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.simple-conversation-avatar {
  text-align: center !important;
  padding: 0 !important;
  width: 2em;
}

.bubble-user {
  background-image: linear-gradient(to right, white, #b3f5ff);
}

.bubble-assistant {
  background-image: linear-gradient(to right, rgb(227, 227, 227), white);
}

.bubble p:last-child {
  margin-bottom: 0;
}

.replay-icon {
  width: 25px;
  height: 25px;
  cursor: pointer;
}

.replay-widget {
  bottom: -20px;
  left: 50%;
}

.message-container .replay-widget {
  opacity: 0;
  transition: opacity 0.3s ease-in-out;
  z-index: 10;
}

.message-container:hover .replay-widget {
  opacity: 0.8;
}
</style>
