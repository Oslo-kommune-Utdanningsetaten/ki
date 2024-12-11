<script setup>
import { ref, watchEffect, useTemplateRef, onMounted } from 'vue'
import Conversation from '@/components/Conversation.vue'
import { submitTextPrompt } from '../utils/httpTools.js'
import SpeechToText from '@/components/SpeechToText.vue'

import AudioMode from '@/components/AudioMode.vue'

const messages = ref([])
const message = ref('')
const lastBotMessage = ref('')
const isProcessingInput = ref(false)
const isStreaming = ref(false)
const isAudioModeEnabled = ref(false)

const props = defineProps({
  bot: {
    type: Object,
    required: true,
  },
})

const textInput = useTemplateRef('text-input')

const resetMessages = () => {
  const { bot } = props
  let fullChoicesText = ''
  if (bot.choices) {
    choicesSorted().forEach(choice => {
      if (choice.selected !== null) {
        fullChoicesText += choice.selected.text + ' '
      }
    })
  }
  messages.value = [
    {
      role: 'system',
      content: bot.prompt + ' ' + fullChoicesText,
    },
  ]
  message.value = ''
  textInput.value.focus()
}

const choicesSorted = () => {
  return props.bot.choices.sort((a, b) => a.order - b.order)
}

const handleMessageInput = messageContent => {
  message.value = message.value + ' ' + messageContent
}

const scrollTo = view => {
  view.value?.scrollIntoView({ behavior: 'smooth' })
}

const sendMessage = async () => {
  const { bot } = props

  messages.value.push({
    role: 'user',
    content: message.value,
  })

  const payload = { uuid: bot.uuid, messages: messages.value }

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

  isProcessingInput.value = true

  await submitTextPrompt(payload, onProgressCallback).then(() => {
    // stream is done, return control to user
    isProcessingInput.value = false
    isStreaming.value = false
    message.value = ''
    lastBotMessage.value = messages.value[messages.value.length - 1].content
    textInput.value.focus()
  })
  scrollTo(textInput)
}

const editMessageAtIndex = index => {
  const messageContent = messages.value[index + 1].content
  // Delete all trailing messages
  messages.value.splice(index + 1)
  message.value = messageContent
  textInput.value.focus()
}

const clipboardAll = bot => {
  const roles = {
    system: 'Ledetekst',
    user: 'Du',
    assistant: 'Bot',
  }
  const omitFirst = !bot.prompt_visibility && copy_text.length > 0
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

const handleToggleAudioMode = () => {
  isAudioModeEnabled.value = !isAudioModeEnabled.value
}

const handleTranscriptReceived = transcript => {
  message.value = transcript
  sendMessage()
}

onMounted(async () => {
  resetMessages()
  textInput.value.focus()
})
</script>

<template>
  <AudioMode
    v-if="isAudioModeEnabled"
    :readOutLoud="lastBotMessage"
    :onTranscriptReceived="handleTranscriptReceived"
  />

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
        aria-label="Skriv her. Ikke legg inn personlige og sensitive opplysninger."
        v-model="message"
        class="form-control"
        placeholder="Skriv her. Ikke legg inn personlige og sensitive opplysninger."
        @keypress.enter.exact="sendMessage()"
      ></textarea>
      <div class="card">
        <div class="card-body bg-body-tertiary">
          <SpeechToText :onMessageReceived="handleMessageInput" />

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
          <div>
            <small>
              Husk at en AI ikke er et menneske og kan skrive ting som ikke stemmer med
              virkeligheten, og den gir ikke beskjed om når den gjør det.
            </small>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div>&nbsp;</div>
</template>
