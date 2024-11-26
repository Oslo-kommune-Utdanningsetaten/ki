<script setup>
import { ref, watchEffect, watch } from 'vue'
import BotAvatar from '@/components/BotAvatar.vue'
import SpeechSynthesizer from '@/components/SpeechSynthesizer.vue'
import { renderMessage } from '../utils/markdownTools.js'

const props = defineProps({
  messages: Array,
  isProcessingInput: Boolean,
  isStreaming: Boolean,
  bot: Object,
  handleEditMessageAtIndex: Function,
})

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
          >
            {{ aMessage.content }}
          </div>

          <div class="widget-container position-absolute d-flex">
            <!-- Edit widget -->
            <a
              v-if="!props.bot.img_bot"
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
          <BotAvatar :avatar_scheme="props.bot.avatar_scheme" />
        </div>

        <div class="w-60 position-relative">
          <div
            class="position-relative bg-light p-3 border"
            :class="`speech-bubble-${aMessage.role}`"
          >
            <div v-if="isProcessingInput && !isStreaming && messageIndex === messages.length - 1">
              <span class="spinner-border spinner-border-sm me-2" role="status"></span>
              <span v-if="props.bot.img_bot">Vent litt mens jeg prøver å lage bildet</span>
            </div>
            <div v-else>
              <div
                v-html="
                  renderMessage(
                    `${bot.img_bot ? '<strong>Ledeteksten jeg brukte:</strong><br/> ' : ''}` +
                      aMessage.content
                  )
                "
              ></div>
              <span
                v-if="isStreaming"
                class="spinner-border spinner-border-sm me-2"
                role="status"
              ></span>
              <div v-if="aMessage.imageUrl">
                <img :src="aMessage.imageUrl" class="img-fluid" alt="Bilde" />
              </div>
            </div>
          </div>

          <div class="widget-container position-absolute d-flex">
            <!-- Image in new tab -->
            <a
              v-if="props.bot.img_bot"
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
</style>
