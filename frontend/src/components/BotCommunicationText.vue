<script setup>
import { ref, useTemplateRef, onMounted, watch } from 'vue'
import { store } from '../store.js'
import Conversation from '@/components/Conversation.vue'
import { submitTextPrompt } from '../utils/httpTools.js'
import SpeechToText from '@/components/SpeechToText.vue'

const messages = ref([])
const message = ref('')
const isProcessingInput = ref(false)
const isStreaming = ref(false)
const textInput = useTemplateRef('text-input')
const maxMessageLength = 15000

const props = defineProps({
  bot: {
    type: Object,
    required: true,
  },
  systemPrompt: {
    type: String,
  },
})

const resetMessages = () => {
  messages.value = [
    {
      role: 'system',
      content: props.systemPrompt,
    },
  ]
  message.value = ''
}

watch(
  () => props.systemPrompt,
  () => {
    resetMessages()
  },
  { immediate: true }
)

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

const scrollTo = view => {
  view.value?.scrollIntoView({ behavior: 'smooth' })
}

const onProgressCallback = streamedText => {
  isStreaming.value = true
  if (messages.value[messages.value.length - 1].role === 'user') {
    messages.value.push({
      role: 'assistant',
      content: streamedText,
    })
  } else {
    messages.value[messages.value.length - 1].content = streamedText
  }
}

const sendMessage = async () => {
  const { bot } = props

  messages.value.push({
    role: 'user',
    content: message.value,
  })

  const data = { uuid: bot.uuid, messages: messages.value }
  isProcessingInput.value = true

  await submitTextPrompt(data, onProgressCallback).then(() => {
    // stream is done, return control to user
    isProcessingInput.value = false
    isStreaming.value = false
    message.value = ''
    textInput.value.focus()
  })
  scrollTo(textInput)
}

const editMessageAtIndex = index => {
  const textToEdit = messages.value[index + 1].content
  messages.value.splice(index + 1) // Delete all trailing messages
  message.value = textToEdit
  textInput.value.focus()
}

const clipboardAll = bot => {
  const roles = {
    system: 'Ledetekst',
    user: 'Du',
    assistant: 'Bot',
  }
  const omitFirst = !bot.prompt_visibility && messages.value.length > 0
  const sourceMessages = omitFirst ? messages.value.slice(1) : messages.value
  const textToCopy = sourceMessages
    .map(message => `${roles[message.role]}: ${message.content}`)
    .join('\n')
  try {
    navigator.clipboard.writeText(textToCopy)
  } catch (error) {
    console.log(error)
  }
}

onMounted(async () => {
  resetMessages()
  textInput.value.focus()
})
</script>

<template>
  <div>
    <Conversation
      :messages="messages.slice(1, messages.length)"
      :bot="props.bot"
      :isProcessingInput="isProcessingInput"
      :isStreaming="isStreaming"
      :handleEditMessageAtIndex="editMessageAtIndex"
    />

    <div class="mt-3" :class="{ 'd-none': isProcessingInput }">
      <textarea
        ref="text-input"
        type="text"
        rows="5"
        aria-label="Skriv her. Ikke legg inn personlige eller sensitive opplysninger."
        v-model="message"
        class="form-control"
        placeholder="Skriv her. Ikke legg inn personlige eller sensitive opplysninger."
        @paste="handlePaste()"
        @keypress.enter.exact="sendMessage()"
      ></textarea>

      <div class="card z-n1">
        <div
          class="card-body bg-body-tertiary d-flex flex-wrap align-items-center gap-1 button-container"
        >
          <SpeechToText v-if="!bot.is_audio_enabled" :onMessageReceived="handleMessageInput" />

          <button
            class="btn oslo-btn-primary"
            type="button"
            id="button-send"
            @click="sendMessage()"
          >
            Send!
          </button>

          <button
            class="btn oslo-btn-secondary"
            type="button"
            id="button-new"
            @click="resetMessages()"
          >
            Ny samtale
          </button>

          <button
            class="btn oslo-btn-secondary"
            type="button"
            id="button-clipboard"
            @click="clipboardAll(bot)"
          >
            <img src="@/components/icons/copy.svg" alt="" />
            Kopier samtalen
          </button>
        </div>

        <div class="card-body bg-body-tertiary pt-0">
          <small>
            Husk at en AI ikke er et menneske og kan gi svar som ikke stemmer med virkeligheten.
          </small>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.button-container > *:first-child {
  margin-left: 0 !important;
}
</style>
