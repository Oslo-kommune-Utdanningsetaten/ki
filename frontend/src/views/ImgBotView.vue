<script setup>
import { RouterLink, useRoute } from 'vue-router'
import { axiosInstance as axios } from '../clients'
import { ref, watchEffect } from 'vue'
import SpeechToText from '@/components/SpeechToText.vue'
import Conversation from '@/components/Conversation.vue'
import { getCookie } from '../utils/httpTools.js'

const route = useRoute()
const bot = ref({})
const messages = ref([])
const message = ref('')
const isProcessingInput = ref(false)
const textInput = ref(null)

const getBot = async () => {
  try {
    const { data } = await axios.get('/api/bot_info/' + route.params.id)
    bot.value = data.bot
  } catch (error) {
    console.log(error)
  }
}

const resetMessages = () => {
  message.value = ''
  messages.value = []
}

const handleMessageInput = messageContent => {
  message.value = message.value + ' ' + messageContent
}

const editMessageAtIndex = index => {
  console.log('editMessageAtIndex', index)
}

const sendMessage = async () => {
  messages.value.push(
    {
      role: 'user',
      content: message.value,
    },
    {
      role: 'assistant',
      content: '',
      imageUrl: '',
    }
  )
  try {
    isProcessingInput.value = true
    const { data } = await axios.post(
      '/api/send_img_message',
      {
        uuid: bot.value.uuid,
        prompt: message.value,
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
      }
    )
    message.value = data.revised_prompt
    // patch the last message with the revised prompt and image url
    messages.value[messages.value.length - 1].content = data.revised_prompt
    messages.value[messages.value.length - 1].imageUrl = data.url
    isProcessingInput.value = false
  } catch (error) {
    console.log(error)
  }
}

watchEffect(() => {
  getBot()
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
