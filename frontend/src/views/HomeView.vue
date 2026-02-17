<script setup>
import { axiosInstance as axios } from '../clients'
import { ref, watchEffect, computed } from 'vue'
import { onMounted } from 'vue'
import BotSelector from '@/components/BotSelector.vue'

const bots = ref([])
const status = ref(null)
const isBotFilteringEnabled = ref(false)
const tagCategories = ref([])
const loginUserName = ref('')
const loginUserPassword = ref('')
const showPassword = ref(false)

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
</script>

<template>
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
      <a href="/auth/feidelogin" role="button" class="btn btn-primary">Logg inn</a>
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
    <div v-if="bots.length === 0">
      <div class="card">
        <div class="card-body">
          <h5 class="card-text">Du har ikke fått tilgang til noen boter</h5>
        </div>
      </div>
    </div>

    <BotSelector
      v-else
      :bots="bots"
      :isBotFilteringEnabled="isBotFilteringEnabled"
      :tagCategories="tagCategories"
    />
  </div>
</template>
