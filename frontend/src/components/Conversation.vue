<script setup>
import { nextTick, watch } from 'vue'
import BotAvatar from '@/components/BotAvatar.vue'
import SpeechSynthesizer from '@/components/SpeechSynthesizer.vue'
import { renderMessage } from '../utils/renderTools.js'

const props = defineProps({
  messages: Array,
  isProcessingInput: Boolean,
  isStreaming: Boolean,
  bot: Object,
  handleEditMessageAtIndex: Function,
})

const scrollToBottom = () => {
  nextTick(() => {
    window.scrollTo({
      top: document.body.scrollHeight,
      behavior: 'smooth',
    })
  })
}

watch(() => props.messages, scrollToBottom, { deep: true })

const copyToclipboard = textToCopy => {
  try {
    navigator.clipboard.writeText(textToCopy)
  } catch (error) {
    console.log(error)
  }
}

const editMessageAtIndex = index => {
  props.handleEditMessageAtIndex(index)
}
</script>

<template>
  <div v-if="props.messages.length" class="card mt-3 p-3">
    <div
      v-for="(aMessage, messageIndex) in props.messages"
      :key="messageIndex"
      class="message-container mb-4 mt-1"
    >
      <div v-if="aMessage.role === 'user'" class="d-flex justify-content-end align-items-end">
        <!-- User -->
        <div class="w-60 position-relative">
          <div
            class="position-relative p-3 border oslo-bg-primary"
            :class="`speech-bubble-${aMessage.role}`"
            v-html="renderMessage(aMessage.content)"
          ></div>

          <div class="widget-container position-absolute d-flex">
            <!-- Edit widget -->
            <a
              v-if="!props.bot.imgBot"
              class="message-widget"
              title="Rediger ledetekst"
              name="editMessageAtIndex"
              @click="editMessageAtIndex(messageIndex)"
              :class="{ invisible: props.isProcessingInput }"
            >
              <img class="oslo-fill-dark-black" src="@/components/icons/edit.svg" alt="rediger" />
            </a>
            <!-- Copy to clipboard widget -->
            <a
              class="message-widget"
              name="copyToclipboard"
              title="Kopier til utklippstavlen"
              @click="copyToclipboard(aMessage.content)"
            >
              <img class="oslo-fill-dark-black" src="@/components/icons/copy.svg" alt="kopier" />
            </a>
            <!-- Speech synth widget -->
            <SpeechSynthesizer
              v-if="!props.isProcessingInput"
              :textInput="aMessage.content"
              class="message-widget"
              title="Spill av"
            />
          </div>
        </div>

        <div class="avatar ms-2">
          <img alt="User Avatar" class="ms-2" src="@/components/icons/user.svg" />
        </div>
      </div>

      <!-- Assistant -->
      <div v-else class="d-flex justify-content-start align-items-end">
        <div class="avatar me-3">
          <BotAvatar :avatarScheme="props.bot.avatarScheme" />
        </div>

        <div class="w-60 position-relative">
          <div
            class="position-relative bg-light p-3 border"
            :class="`speech-bubble-${aMessage.role}`"
          >
            <div
              v-if="aMessage.content === '' && messageIndex === props.messages.length - 1"
              aria-hidden="true"
            >
              <p class="placeholder-glow" aria-hidden="true">
                <span class="placeholder col-12 bg-secondary"></span>
                <span class="placeholder col-12 bg-secondary"></span>
                <span class="placeholder col-7 bg-secondary"></span>
              </p>
            </div>
            <div v-else>
              <div v-html="renderMessage(aMessage.content)"></div>
              <div v-if="aMessage.imageUrl">
                <img :src="aMessage.imageUrl" class="img-fluid" alt="Bilde" />
              </div>
            </div>
          </div>

          <div class="widget-container position-absolute d-flex">
            <!-- Image in new tab -->
            <a
              v-if="props.bot.imgBot"
              :href="aMessage.imageUrl"
              target="_blank"
              class="message-widget"
              title="Åpne bildet i ny fane"
            >
              <img src="@/components/icons/new_window.svg" alt="Åpne bilde i nytt vindu" />
            </a>
            <!-- Copy to clipboard widget -->
            <a
              class="message-widget"
              name="copyToclipboard"
              title="Kopier til utklippstavlen"
              @click="copyToclipboard(aMessage.content)"
            >
              <img class="oslo-fill-dark-black" src="@/components/icons/copy.svg" alt="kopier" />
            </a>
            <!-- Speech synth widget -->
            <SpeechSynthesizer
              v-if="!props.isProcessingInput"
              :textInput="aMessage.content"
              class="message-widget"
              title="Spill av"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.widget-container {
  bottom: -27px;
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

.speech-bubble-assistant :deep(li:not(:first-child)) {
  padding-top: 0.8rem;
}
</style>
