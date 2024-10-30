<script setup>
import { RouterLink, useRoute } from 'vue-router'
import axios from 'axios'
import { ref, watchEffect } from 'vue'
import BotAvatar from '@/components/BotAvatar.vue'

const route = useRoute()
const bot = ref({})
const botId = ref(0)
const prompt = ref('')
const insertPrompt = ref('')
const image = ref('')
const spinner = ref(false)
botId.value = route.params.id

const textInput = ref(null) // Add a ref for the text input element

const startpromt = async () => {
  try {
    const { data } = await axios.get('/api/bot_info/' + botId.value)
    bot.value = data.bot
  } catch (error) {
    console.log(error)
  }
}

const resetMessages = () => {
  prompt.value = ''
  image.value = ''
  insertPrompt.value = ''
}

const sendMessage = async () => {
  try {
    prompt.value = insertPrompt.value
    image.value = ''
    spinner.value = true
    const { data } = await axios.post(
      '/api/send_img_message',
      {
        uuid: botId.value,
        prompt: prompt.value,
      },
      {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
      }
    )
    image.value = data
    insertPrompt.value = data.revised_prompt
    spinner.value = false
  } catch (error) {
    console.log(error)
  }
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

watchEffect(() => {
  startpromt()
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

  <div v-if="spinner || image.url || image.msg" class="card">
    <ul class="list-group list-group-flush">
      <li class="container-fluid list-group-item response user">
        <span class="row">
          <div class="col-1 avatar">
            <img src="@/components/icons/user.svg" alt="du:" />
          </div>
          <div class="col">
            {{ prompt }}
          </div>
          <div class="col-1 clipboard">
            <a href="#" @click="clipboard(msg_nr)">
              <img src="@/components/icons/clipboard.svg" alt="kopier" />
            </a>
          </div>
        </span>
      </li>
      <li class="container-fluid list-group-item response assistant">
        <span class="row">
          <div class="col-1 avatar">
            <BotAvatar :avatar_scheme="bot.avatar_scheme" alt="bot:" />
          </div>
          <div v-if="spinner" class="col">
            <span class="spinner-border spinner-border-sm" role="status"></span>
            <span class="ms-3">Vent litt mens jeg lager bildet ditt</span>
          </div>
          <div v-if="image.url" class="col-4">
            <img :src="image.url" class="img-fluid" alt="Bilde" />
          </div>
          <div v-if="image.url" class="col-6"></div>
          <div v-if="image.url" class="col-1 clipboard">
            <a :href="image.url" target="_blank">
              <img src="@/components/icons/new_window.svg" alt="åpne i nytt vindu" />
            </a>
          </div>
          <div v-if="image.msg" class="col">
            {{ image.msg }}
          </div>
        </span>
      </li>
    </ul>
  </div>

  <div id="input_line" class="mt-3">
    <div v-if="image != ''">Du kan redigere ledeteksten jeg brukte for å forbedre bildet:</div>
    <textarea
      id="text-input"
      ref="textInput"
      type="text"
      rows="5"
      aria-label="Forklar hva bildet skal vise. Ikke legg inn personlige og sensitive opplysninger."
      v-model="insertPrompt"
      class="form-control"
      placeholder="Forklar hva bildet skal vise. Ikke legg inn personlige og sensitive opplysninger."
      @keypress.enter.exact="sendMessage()"
    ></textarea>
    <div class="card">
      <div class="card-body bg-body-tertiary">
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
