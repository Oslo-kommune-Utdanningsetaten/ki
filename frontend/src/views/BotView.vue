<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { ref, watchEffect, useTemplateRef, onMounted } from 'vue'
import { store } from '../store.js'
import BotAvatar from '@/components/BotAvatar.vue'
import AudioWave from '@/components/AudioWave.vue'
import SpeechSynthesizer from '@/components/SpeechSynthesizer.vue'

const route = useRoute()
const router = useRouter()
const bot = ref({})
const messages = ref([])
const message = ref('')
const botId = ref(0)
botId.value = route.params.id
const isProcessingInput = ref(false)
const showSystemPrompt = ref(false)

// Does the browser support speech recognition
const isBrowserSpeechEnabled = ref(false)
// Has the user granted permission to use the microphone
let microphonePermissionStatus = ref('denied')
// Are we currently listening for speech input
const isSpeechRecognitionActive = ref(false)
// Speech recognition session
let speechRecognitionSession

const textInput = useTemplateRef('text-input') // Add a ref for the text input element

const choicesSorted = () => {
  return bot.value.choices.sort((a, b) => a.order - b.order)
}

const optionsSorted = choice => {
  return choice.options.sort((a, b) => a.order - b.order)
}

const startpromt = async () => {
  try {
    const { data } = await axios.get('/api/bot_info/' + botId.value)
    bot.value = data.bot
    resetMessages()
    // messages.value = [{
    //   "role": "system",
    //   "content": bot.value.prompt,
    // }];
  } catch (error) {
    console.log(error)
  }
}

const resetMessages = () => {
  let fullChoicesText = ''
  if (bot.value.choices) {
    choicesSorted().forEach(choice => {
      if (choice.selected !== null) {
        // fullChoicesText += choice.text + ' ' + choice.selected.text + ' ';
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

  const data = { uuid: botId.value, messages: messages.value }
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

const getCookie = name => {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

const editPrompt = response_nr => {
  messages.value.splice(response_nr + 1)
  message.value = messages.value.pop()['content']
  isProcessingInput.value = false
}

const toggleStartPrompt = () => {
  showSystemPrompt.value = !showSystemPrompt.value
}

const deleteBot = () => {
  axios
    .delete('/api/bot_info/' + botId.value)
    .then(response => {
      store.addMessage('Boten er nå slettet', 'info')
      router.push({ name: 'home' })
    })
    .catch(error => {
      console.log(error)
    })
}

const clipboard = response_nr => {
  try {
    navigator.clipboard.writeText(messages.value[response_nr].content)
  } catch (error) {
    console.log(error)
  }
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

const renderMessage = aMessage => {
  if (aMessage.role === 'assistant') {
    return DOMPurify.sanitize(marked.parse(aMessage.content))
  }
  return aMessage.content
}

const checkmicrophonePermissionStatus = async () => {
  const permission = await navigator.permissions.query({ name: 'microphone' })
  microphonePermissionStatus.value = permission.state
  console.info('Microphone permission:', microphonePermissionStatus.value)
}

const toggleSpeechInput = () => {
  // Fail early if speech recognition has not been set up
  if (!speechRecognitionSession) return
  if (isSpeechRecognitionActive.value) {
    speechRecognitionSession.stop()
  } else {
    speechRecognitionSession.start()
  }
}

const configureSpeechRecognition = () => {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

  if (SpeechRecognition) {
    isBrowserSpeechEnabled.value = true

    speechRecognitionSession = new SpeechRecognition()
    speechRecognitionSession.lang = navigator.language || navigator.userLanguage
    speechRecognitionSession.interimResults = true
    speechRecognitionSession.maxAlternatives = 1

    // Set up event handlers
    speechRecognitionSession.onstart = () => {
      isSpeechRecognitionActive.value = true
    }

    speechRecognitionSession.onresult = event => {
      const transcript = event.results[0][0].transcript
      message.value = transcript
      isSpeechRecognitionActive.value = false
    }

    speechRecognitionSession.onerror = event => {
      console.error('Speech recognition error:', event.error)
      isSpeechRecognitionActive.value = false
    }

    speechRecognitionSession.onend = () => {
      isSpeechRecognitionActive.value = false
      // Speech is assumend finished, now send the message
      if (message.value !== '') {
        sendMessage()
      }
    }
  } else {
    isBrowserSpeechEnabled.value = false
    console.info('Speech recognition not supported in this browser.')
  }
}

watchEffect(() => {
  startpromt()
  checkmicrophonePermissionStatus()
})

onMounted(() => {
  configureSpeechRecognition()
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
    class="me-auto btn oslo-btn-secondary"
    @click="toggleStartPrompt"
  >
    Vis ledetekst
  </button>

  <div class="card">
    <ul class="list-group list-group-flush">
      <span v-for="(message_line, msg_nr) in messages" :key="msg_nr">
        <li
          v-if="message_line.role != 'system' || showSystemPrompt"
          class="container-fluid list-group-item response"
          :class="message_line.role"
        >
          <span class="row">
            <div class="col-1 avatar">
              <img
                v-if="message_line.role === 'system'"
                src="@/components/icons/system.svg"
                alt="ledetekst:"
              />
              <img
                v-if="message_line.role === 'user'"
                src="@/components/icons/user.svg"
                alt="du:"
              />
              <BotAvatar
                v-if="message_line.role === 'assistant'"
                :avatar_scheme="bot.avatar_scheme"
              />
            </div>
            <div class="col">
              <span
                v-html="renderMessage(message_line, msg_nr)"
                class="chat"
                :class="msg_nr === messages.length - 1 && isProcessingInput ? 'type-writer' : ''"
              ></span>
            </div>
            <div class="col-1">
              <div class="d-flex justify-content-end">
                <div class="edit-link" :class="{ invisible: isProcessingInput }">
                  <a v-if="message_line.role === 'user'" href="#" @click="editPrompt(msg_nr)">
                    <img src="@/components/icons/rediger.svg" alt="rediger" />
                  </a>
                </div>
                <div class="clipboard">
                  <a href="#" @click="clipboard(msg_nr)">
                    <img src="@/components/icons/clipboard.svg" alt="kopier" />
                  </a>
                </div>
                <div class="speech-synth">
                  <SpeechSynthesizer v-if="!isProcessingInput" :textInput="message_line.content" />
                </div>
              </div>
            </div>
          </span>
        </li>
      </span>
    </ul>
  </div>
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
        <button
          v-if="isBrowserSpeechEnabled"
          @click="toggleSpeechInput"
          class="btn oslo-btn-secondary mic-button"
          :title="
            microphonePermissionStatus === 'denied'
              ? 'Nettleseren har ikke tilgang til mikrofonen'
              : 'Trykk for å snakke inn tekst'
          "
          :disabled="microphonePermissionStatus === 'denied'"
        >
          <AudioWave v-if="isSpeechRecognitionActive" />
          <img v-else src="@/components/icons/microphone.svg" class="mic-icon" alt="mikrofon" />
        </button>

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
          <img src="@/components/icons/clipboard.svg" alt="" />
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

<style scoped>
.mic-button {
  pointer-events: auto;
}

.mic-icon {
  transform: scale(1.2);
  display: inline-block;
  transition: transform 0.2s ease-out;
}

.mic-button:hover .mic-icon {
  transform: scale(1.5);
}
</style>
