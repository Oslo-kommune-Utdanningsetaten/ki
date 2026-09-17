<script setup>
import { computed } from 'vue'
import BotAvatar from '@/components/BotAvatar.vue'
import SpeechSynthesizer from '@/components/SpeechSynthesizer.vue'
import { renderMessage } from '../utils/renderTools.js'

const props = defineProps({
  message: { type: Object, required: true },
  messageIndex: { type: Number, required: true },
  isLast: { type: Boolean, default: false },
  isProcessingInput: { type: Boolean, default: false },
  bot: { type: Object, required: true },
  handleEditMessageAtIndex: { type: Function, required: true },
})

const renderedContent = computed(() => renderMessage(props.message.content))

const copyToclipboard = () => {
  try {
    navigator.clipboard.writeText(props.message.content)
  } catch (error) {
    console.log(error)
  }
}

const editMessageAtIndex = () => {
  props.handleEditMessageAtIndex(props.messageIndex)
}
</script>

<template>
  <div class="message-container mb-4 mt-1">
    <!-- User -->
    <div v-if="message.role === 'user'" class="d-flex justify-content-end align-items-end">
      <div class="w-60 position-relative">
        <div
          class="position-relative p-3 border bg-primary speech-bubble-user"
          v-html="renderedContent"
        ></div>

        <div class="widget-container position-absolute d-flex">
          <a
            v-if="!bot.imgBot"
            class="message-widget"
            title="Rediger ledetekst"
            name="editMessageAtIndex"
            @click="editMessageAtIndex"
            :class="{ invisible: isProcessingInput }"
          >
            <img class="oslo-fill-dark-black" src="@/components/icons/edit.svg" alt="rediger" />
          </a>
          <a
            class="message-widget"
            name="copyToclipboard"
            title="Kopier til utklippstavlen"
            @click="copyToclipboard"
          >
            <img class="oslo-fill-dark-black" src="@/components/icons/copy.svg" alt="kopier" />
          </a>
          <SpeechSynthesizer
            v-if="!isProcessingInput"
            :textInput="message.content"
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
        <BotAvatar :avatarScheme="bot.avatarScheme" />
      </div>

      <div class="w-60 position-relative">
        <div class="position-relative bg-light p-3 border speech-bubble-assistant">
          <div v-if="message.content === '' && isLast" aria-hidden="true">
            <p class="placeholder-glow" aria-hidden="true">
              <span class="placeholder col-12 bg-secondary"></span>
              <span class="placeholder col-12 bg-secondary"></span>
              <span class="placeholder col-7 bg-secondary"></span>
            </p>
          </div>
          <div v-else>
            <div v-html="renderedContent"></div>
            <div v-if="message.imageUrl">
              <img :src="message.imageUrl" class="img-fluid" alt="Bilde" />
            </div>
          </div>
        </div>

        <div class="widget-container position-absolute d-flex">
          <a
            v-if="bot.imgBot"
            :href="message.imageUrl"
            target="_blank"
            class="message-widget"
            title="Åpne bildet i ny fane"
          >
            <img src="@/components/icons/new_window.svg" alt="Åpne bilde i nytt vindu" />
          </a>
          <a
            class="message-widget"
            name="copyToclipboard"
            title="Kopier til utklippstavlen"
            @click="copyToclipboard"
          >
            <img class="oslo-fill-dark-black" src="@/components/icons/copy.svg" alt="kopier" />
          </a>
          <SpeechSynthesizer
            v-if="!isProcessingInput"
            :textInput="message.content"
            class="message-widget"
            title="Spill av"
          />
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
