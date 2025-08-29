<script setup>
import { RouterLink } from 'vue-router'
import { axiosInstance as axios } from '../clients'
import { ref, watchEffect, computed } from 'vue'
import { store } from '../store.js'
import { submitLogin } from '../utils/httpTools.js'
import { onMounted } from 'vue'
import BotSelector from '@/components/BotSelector.vue'

const bots = ref([])
const status = ref(null)
// const filterMode = ref('favorites')
const isBotFilteringEnabled = ref(false)
// const isFilterSelected = ref(false)
// const activeBot = ref(null)
const tagCategories = ref([])
const loginUserName = ref('')
const loginUserPassword = ref('')
const showPassword = ref(false)

// const route = useRoute()

watchEffect(() => {
  getBots()
})

onMounted(() => {
  const loginModalEl = document.getElementById('loginModal')
  if (loginModalEl) {
    loginModalEl.addEventListener('hidden.bs.modal', onLoginModalClosed)
  }
})

async function getBots() {
  try {
    const { data } = await axios.get('/api/user_bots')
    bots.value = data.bots || []
    status.value = data.status || ''
    isBotFilteringEnabled.value = Boolean(data.isBotFilteringEnabled) || false
    tagCategories.value = data.tagCategories || []
  } catch (error) {
    if (error.response && error.response.status === 401) {
      window.location.href = '/auth/feidelogin'
    } else {
      console.log(error)
    }
  }
}

const onLoginModalClosed = () => {
  loginUserName.value = ''
  loginUserPassword.value = ''
  showPassword.value = false
}

const sendLogin = async () => {
  try {
    const { data } = await submitLogin({
      username: loginUserName.value,
      password: loginUserPassword.value,
    })

    // Check if login was successful

    if (data.status === 'ok') {
      loginUserName.value = ''
      loginUserPassword.value = ''
      window.location.href = '/'
    } else {
      store.addMessage(data.message, 'error')
      window.location.href = '/'
    }
  } catch (error) {
    console.error('Error during login:', error)
  }
}
</script>
<template>
  <!-- Modal -->
  <div class="modal fade" id="loginModal" tabindex="-1" aria-labelledby="loginLabel">
    <div class="modal-dialog">
      <div class="modal-content">
        <form @submit.prevent="sendLogin">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="loginLabel">Logg inn</h1>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <input
                type="text"
                class="form-control"
                id="username"
                v-model="loginUserName"
                required
                placeholder="Brukernavn"
              />
              <div class="input-group mt-2">
                <input
                  :type="showPassword ? 'text' : 'password'"
                  class="form-control"
                  id="password"
                  v-model="loginUserPassword"
                  placeholder="Passord"
                />
                <button
                  type="button"
                  class="btn btn-outline-secondary mb-0"
                  @click="(showPassword = !showPassword)"
                >
                  <img
                    v-if="showPassword"
                    src="@/components/icons/eye-hide.svg"
                    alt="Skjul passord"
                  />
                  <img v-else src="@/components/icons/eye-show.svg" alt="Vis passord" />
                </button>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="submit" class="btn oslo-btn-primary" data-bs-dismiss="modal">
              Logg inn
            </button>
            <button type="button" class="btn oslo-btn-secondary" data-bs-dismiss="modal">
              Lukk
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <div v-if="status != 'ok'" class="mb-3">
    <p>
      KI i Osloskolen er en løsning for å gi lærere og elever i Osloskolens tilgang til å bruke
      kunstig intelligens på en trygg måte. Løsningen baserer seg på Azure OpenAI. Azure OpenAI er
      Microsoft sin utgave av OpenAI sine ulike språkmodeller. Selv om løsningen er lagt bak
      FEIDE-pålogging, lagrer den ikke persondata. Feide-påloggingen benyttes kun til tilgangs- og
      kostnadskontroll, slik at elever og lærere i Osloskolen kan bruke denne teknologien på en
      trygg måte.
      <a
        href="https://aktuelt.osloskolen.no/larerik-bruk-av-laringsteknologi/informasjonssikkerhet-og-personvern/feide-tjenester/ki/"
        target="_blank"
      >
        Her kan du lese mer om informasjonssikkerhet og personvern i løsningen.
      </a>
    </p>
    <p>
      Osloskolens løsning er inspirert av Randabergskolens AI-løsning. Løsningen utvikles av
      Utdanningsetaten og veilederteamet for bruk av læringsteknologi i Osloskolen.
    </p>
    <div v-if="status === 'not_feide'">
      <a href="/auth/feidelogin" role="button" class="btn oslo-btn-primary">Logg inn</a>
    </div>
    <div v-if="status === 'not_feide'" class="mt-2">
      <button
        type="button"
        class="btn btn-secondary"
        data-bs-toggle="modal"
        data-bs-target="#loginModal"
      >
        Logg inn med demobruker
      </button>
    </div>
    <div v-else-if="status === 'not_school'">
      <div class="card">
        <div class="card-body">
          <h5 class="card-text">Elever på skolen din har ikke tilgang til denne tjenesten.</h5>
        </div>
      </div>
    </div>
    <div class="mt-3">
      <p>
        <a
          href="https://uustatus.no/nb/erklaringer/publisert/a049250e-d0fb-4510-8f7c-29427e8876e8"
          target="_blank"
        >
          Tilgjengelighetserklæring
        </a>
      </p>
    </div>
  </div>
  <div v-else class="mb-3">
    <p>
      Dette er en trygg og sikker måte å bruke kunstig intelligens på. Løsningen bruker ikke eller
      lagrer personopplysninger. Les mer under "Om tjenesten"
    </p>
    <div v-if="bots.length === 0">
      <div class="card">
        <div class="card-body">
          <h5 class="card-text">Du har ikke fått tilgang til noen boter</h5>
        </div>
      </div>
    </div>

    <BotSelector
      :bots="bots"
      :isBotFilteringEnabled="isBotFilteringEnabled"
      :tagCategories="tagCategories"
    />
  </div>
</template>
