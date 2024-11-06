<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { ref, watchEffect, useTemplateRef, onMounted } from 'vue'
import { store } from '../store.js'
import BotAvatar from '@/components/BotAvatar.vue'
import Conversation from '@/components/Conversation.vue'
import { renderMessage, getCookie } from '../utils.js'
import SpeechToText from '@/components/SpeechToText.vue'

const route = useRoute()
const router = useRouter()
const bot = ref({})
const messages = ref([])
const message = ref('')
const isProcessingInput = ref(false)
const showSystemPrompt = ref(false)

const textInput = useTemplateRef('text-input')

const choicesSorted = () => {
  return bot.value.choices.sort((a, b) => a.order - b.order)
}

const optionsSorted = choice => {
  return choice.options.sort((a, b) => a.order - b.order)
}

const startpromt = async () => {
  try {
    const { data } = await axios.get('/api/bot_info/' + route.params.id)
    bot.value = data.bot
    resetMessages()
  } catch (error) {
    console.log(error)
  }
}

const resetMessages = () => {
  let fullChoicesText = ''
  if (bot.value.choices) {
    choicesSorted().forEach(choice => {
      if (choice.selected !== null) {
        fullChoicesText += choice.selected.text + ' '
      }
    })
  }
  messages.value = [
    {
      role: 'system',
      content: bot.value.prompt + ' ' + fullChoicesText,
    },
  ]
}

const handleMessageInput = (messageContent, isDone) => {
  message.value = messageContent
  if (isDone) {
    sendMessage()
  }
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
    }
  )
  isProcessingInput.value = true

  const data = { uuid: bot.value.uuid, messages: messages.value }
  const handleStreamText = streamedText => {
    messages.value[messages.value.length - 1].content = streamedText
  }
  await callChatStream(data, handleStreamText).then(() => {
    // stream is done, return control to user
    isProcessingInput.value = false
    message.value = ''
    textInput.value.focus() // Set focus to the text input element
  })
}

const callChatStream = async (data, progressCallback) => {
  const csrf = getCookie('csrftoken')
  return await axios
    .post('/api/send_message', data, {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf,
      },
      responseType: 'stream',
      onDownloadProgress: progressEvent => {
        // axios doesn't support streaming on post, so we need to update messages manually on download progress
        progressCallback(progressEvent.event.target.responseText)
      },
    })
    .catch(error => {
      console.error('Something went wrong while streaming the chat response', error)
    })
}

const editMessageAtIndex = index => {
  const messageContent = messages.value[index + 1].content
  // Delete all trailing messages
  messages.value.splice(index + 1)
  message.value = messageContent
  textInput.value.focus() // Set focus to the text input element
}

const toggleStartPrompt = () => {
  showSystemPrompt.value = !showSystemPrompt.value
}

const deleteBot = () => {
  axios
    .delete('/api/bot_info/' + bot.value.uuid)
    .then(() => {
      store.addMessage('Boten er nå slettet', 'info')
      router.push({ name: 'home' })
    })
    .catch(error => {
      console.log(error)
    })
}

const clipboardAll = bot => {
  const roles = {
    system: 'Ledetekst',
    user: 'Du',
    assistant: 'Bot',
  }
  let copy_text = messages.value
  // console.log(copy_text)
  if (!bot.prompt_visibility && copy_text.length > 0) {
    copy_text = messages.value.slice(1)
  }
  // console.log(copy_text)
  try {
    navigator.clipboard.writeText(copy_text.map(x => `${roles[x.role]}: ${x.content}`).join('\n'))
  } catch (error) {
    console.log(error)
  }
}

watchEffect(() => {
  startpromt()
})
</script>

<template>
  <!-- Modal -->
  <div
    class="modal fade"
    id="delete_bot"
    tabindex="-1"
    aria-labelledby="delete_bot_label"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="delete_bot_label">Slette bot</h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">Vi du virkelig slette denne boten?</div>
        <div class="modal-footer">
          <button type="button" class="btn oslo-btn-secondary" data-bs-dismiss="modal">
            Avbryt
          </button>
          <button
            type="button"
            class="btn oslo-btn-warning"
            data-bs-dismiss="modal"
            @click="deleteBot"
          >
            Ja jeg vil slette
          </button>
        </div>
      </div>
    </div>
  </div>

  <div class="d-flex justify-content-end">
    <RouterLink
      v-if="bot.distribute && bot.library"
      class="btn oslo-btn-secondary"
      :to="'/editbot/distribute/' + bot.uuid"
    >
      Gi tilgang
    </RouterLink>
    <RouterLink v-if="bot.edit" class="btn oslo-btn-secondary" :to="'/editbot/edit/' + bot.uuid">
      Rediger bot
    </RouterLink>
    <button
      v-if="bot.edit"
      class="btn oslo-btn-warning"
      data-bs-toggle="modal"
      data-bs-target="#delete_bot"
    >
      Slett bot
    </button>
  </div>

  <div class="p-1">
    <h1 class="h2 mb-3">
      {{ bot.title }}
    </h1>
    <p>
      {{ bot.ingress }}
    </p>

    <div v-if="bot.choices && bot.choices.length" class="card p-3 mb-3">
      <div v-for="choice in choicesSorted()" class="row mb-2">
        <div class="col-4 col-form-label">{{ choice.label }}</div>
        <div class="col-8" role="group">
          <span v-for="option in optionsSorted(choice)" :key="option.id">
            <input
              class="btn-check"
              type="radio"
              :id="`${choice.id}-${option.id}`"
              :value="option"
              v-model="choice.selected"
              @change="resetMessages()"
            />
            <label class="btn oslo-btn-secondary" :for="`${choice.id}-${option.id}`">
              {{ option.label }}
            </label>
          </span>
        </div>
      </div>
    </div>

    <button
      v-if="bot.prompt_visibility"
      class="me-auto btn oslo-btn-secondary ms-0"
      @click="toggleStartPrompt"
    >
      {{ showSystemPrompt ? 'Skjul' : 'Vis' }} ledetekst
    </button>

    <div v-if="showSystemPrompt" class="d-flex justify-content-start align-items-end mt-3">
      <div class="avatar p-2 me-3">
        <BotAvatar :avatar_scheme="bot.avatar_scheme" />
      </div>
      <div class="speech-bubble-assistant position-relative bg-light p-3 border text-right">
        <strong>Dette er instruksene jeg har fått:</strong>
        <p class="mb-0">{{ renderMessage(messages[0].content) }}</p>
      </div>
    </div>
  </div>

  <Conversation
    :messages="messages.slice(1, messages.length)"
    :bot="bot"
    :isProcessingInput="isProcessingInput"
    :handleEditMessageAtIndex="editMessageAtIndex"
  />

  <div id="input_line" class="mt-3" :class="{ 'd-none': isProcessingInput }">
    <textarea
      id="text-input"
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

        <button class="btn oslo-btn-primary" type="button" id="button-send" @click="sendMessage()">
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
            Husk at en AI ikke er et menneske og kan skrive ting som ikke stemmer med virkeligheten,
            og den gir ikke beskjed om når den gjør det.
          </small>
        </div>
      </div>
    </div>
  </div>
  <div>&nbsp;</div>
</template>
