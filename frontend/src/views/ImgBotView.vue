<script setup>
import { RouterLink, useRoute } from 'vue-router'
import { ref, watchEffect } from 'vue'
import SpeechToText from '@/components/SpeechToText.vue'
import Conversation from '@/components/Conversation.vue'
import { getBot, submitImagePrompt } from '../utils/httpTools.js'

const route = useRoute()
const bot = ref({})
const messages = ref([])
const message = ref('')
const isProcessingInput = ref(false)
const textInput = ref(null)
const maxMessageLength = 1500

const resetMessages = () => {
  message.value = ''
  messages.value = []
}

const handleMessageInput = messageContent => {
  message.value = message.value + ' ' + messageContent
}

const handlePaste = () => {
  // Wait for the paste to complete before checking the length
  setTimeout(function () {
    if (message.value.length > maxMessageLength) {
      const originalLength = message.value.length
      message.value = message.value.substring(0, maxMessageLength)
      store.addMessage(
        `Maks antall tegn tillatt er ${maxMessageLength}. Teksten du limte inn ble redusert med ${originalLength - maxMessageLength} tegn.`,
        'warning'
      )
    }
  }, 10)
}

const editMessageAtIndex = index => {
  console.log('editMessageAtIndex', index)
}

const sendMessage = async () => {
  isProcessingInput.value = true
  messages.value.push({
    role: 'user',
    content: message.value,
  })
  const data = {
    uuid: bot.value.uuid,
    messages: new Array(...messages.value),
  }
  // Add a new message to indicate that the bot is working
  messages.value.push({
    role: 'assistant',
    content: '',
    imageUrl: '',
  })
  const { revisedPrompt, imageUrl } = await submitImagePrompt(data)
  // patch the last message with the revised prompt and image url
  messages.value[messages.value.length - 1].content = revisedPrompt
  messages.value[messages.value.length - 1].imageUrl = imageUrl
  // Update text area content with revised prompt
  message.value = revisedPrompt
  isProcessingInput.value = false
}

watchEffect(async () => {
  bot.value = await getBot(route.params.id)
})
</script>

<template>
  <div class="d-flex justify-content-end">
    <RouterLink
      v-if="bot.distribute && bot.library"
      class="btn oslo-btn-secondary"
      :to="'/editbot/distribute/' + bot.uuid"
    >
      Gi tilgang
    </RouterLink>
  </div>
  <h1 class="h2 mb-3">
    {{ bot.title }}
  </h1>
  <p>
    {{ bot.ingress }}
  </p>

  <Conversation
    :messages="messages"
    :bot="bot"
    :isProcessingInput="isProcessingInput"
    :isStreaming="false"
    :handleEditMessageAtIndex="editMessageAtIndex"
  />

  <div class="mt-3">
    <div v-if="messages.length && !isProcessingInput" class="mb-1">
      Du kan redigere ledeteksten for å lage et nytt bilde som ligner:
    </div>
    <textarea
      id="text-input"
      ref="textInput"
      type="text"
      rows="5"
      aria-label="Forklar hva bildet skal vise. Ikke legg inn personlige og sensitive opplysninger."
      v-model="message"
      class="form-control"
      :disabled="isProcessingInput"
      placeholder="Forklar hva bildet skal vise. Ikke legg inn personlige og sensitive opplysninger."
      @paste="handlePaste()"
      @keypress.enter.exact="sendMessage()"
    ></textarea>
    <div class="card">
      <div class="card-body bg-body-tertiary">
        <SpeechToText :onMessageReceived="handleMessageInput" />
        <button class="btn oslo-btn-primary" type="button" id="button-send" @click="sendMessage()">
          Send
        </button>
        <button
          class="btn oslo-btn-secondary"
          type="button"
          id="button-new"
          @click="resetMessages()"
        >
          Start på nytt
        </button>
      </div>
    </div>
  </div>
</template>
