<script setup>
import { ref, watchEffect } from 'vue'
import BotAvatar from '@/components/BotAvatar.vue'
import SpeechSynthesizer from '@/components/SpeechSynthesizer.vue'
import { renderMessage } from '../utils.js'

const attr = defineProps([
  'messages',
  'isProcessingInputAtIndex',
  'bot',
  'handleEditMessageAtIndex',
])
let messages = ref(attr.messages)
let isProcessingInputAtIndex = ref(attr.isProcessingInputAtIndex)
let bot = ref(attr.bot)
let handleEditMessageAtIndex = ref(attr.handleEditMessageAtIndex)

const copyToclipboard = textToCopy => {
  try {
    navigator.clipboard.writeText(textToCopy)
  } catch (error) {
    console.log(error)
  }
}

const editMessageAtIndex = index => {
  handleEditMessageAtIndex.value(index)
}

watchEffect(() => {
  messages.value = attr.messages
  isProcessingInputAtIndex.value = attr.isProcessingInputAtIndex
  bot.value = attr.bot
  handleEditMessageAtIndex.value = attr.handleEditMessageAtIndex
})
</script>

<template>
  <div v-if="messages.length" class="card mt-3 p-3">
    <div
      v-for="(aMessage, messageIndex) in messages"
      :key="messageIndex"
      class="message-container mb-4 mt-1"
    >
      <div v-if="aMessage.role === 'user'" class="d-flex justify-content-end align-items-start">
        <!-- User -->
        <div class="w-60 position-relative text-right">
          <div class="position-relative p-3 border text-right oslo-bg-primary">
            {{ aMessage.content }}
          </div>

          <div class="widget-container position-absolute d-flex">
            <!-- Edit widget -->
            <a
              class="message-widget"
              href="#"
              @click="editMessageAtIndex(messageIndex)"
              :class="{ invisible: isProcessingInputAtIndex > -1 }"
            >
              <img class="oslo-fill-dark-black" src="@/components/icons/edit.svg" alt="rediger" />
            </a>
            <!-- Copy to clipboard widget -->
            <a class="message-widget" href="#" @click="copyToclipboard(aMessage.content)">
              <img class="oslo-fill-dark-black" src="@/components/icons/copy.svg" alt="kopier" />
            </a>
            <!-- Speech synth widget -->
            <SpeechSynthesizer
              v-if="isProcessingInputAtIndex > -1"
              :textInput="aMessage.content"
              class="message-widget"
            />
          </div>
        </div>

        <div class="avatar ms-2">
          <img alt="User Avatar" class="ms-2" src="@/components/icons/user.svg" />
        </div>
      </div>

      <!-- Assistant -->
      <div v-else class="d-flex justify-content-start align-items-start">
        <div class="avatar me-3">
          <BotAvatar :avatar_scheme="bot.avatar_scheme" />
        </div>

        <div class="w-60 position-relative text-right">
          <span
            v-if="isProcessingInputAtIndex === messageIndex + 1"
            class="spinner-border spinner-border-sm"
            role="status"
          ></span>
          <div
            v-else
            class="position-relative bg-light p-3 border text-right"
            v-html="renderMessage(aMessage.content)"
          ></div>
          <div class="widget-container position-absolute d-flex">
            <!-- Copy to clipboard widget -->
            <a class="message-widget" href="#" @click="copyToclipboard(aMessage.content)">
              <img class="oslo-fill-dark-black" src="@/components/icons/copy.svg" alt="kopier" />
            </a>
            <!-- Speech synth widget -->
            <SpeechSynthesizer
              v-if="isProcessingInputAtIndex > -1"
              :textInput="aMessage.content"
              class="message-widget"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.widget-container {
  bottom: -30px;
  right: 10px;
}

.message-container .widget-container {
  opacity: 0;
  transition: opacity 0.3s ease-in-out;
  z-index: 10;
}

.message-container:hover .widget-container {
  opacity: 0.8;
}
</style>
