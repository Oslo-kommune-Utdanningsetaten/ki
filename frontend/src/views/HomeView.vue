<script setup>
import { RouterLink } from 'vue-router'
import { axiosInstance as axios } from '../clients'
import { ref, watchEffect, computed } from 'vue'
import { store } from '../store.js'
import BotAvatar from '@/components/BotAvatar.vue'
import { submitLogin } from '../utils/httpTools.js'
import { onMounted } from 'vue'

const bots = ref([])
const status = ref(null)
const showLibrary = ref(false)
const isBotFilteringEnabled = ref(false)
const isFilterWidgetVisible = ref(false)
const activeBot = ref(null)
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
    isBotFilteringEnabled.value = data.isBotFilteringEnabled || ''
    tagCategories.value = data.tagCategories || {}
  } catch (error) {
    if (error.response && error.response.status === 401) {
      window.location.href = '/auth/feidelogin'
    } else {
      console.log(error)
    }
  }
}

const filterBots = computed(() => {
  bots.value.sort((a, b) => b.mandatory - a.mandatory || a.botTitle.localeCompare(b.botTitle))
  if (!store.isEmployee && !store.isAdmin) {
    return bots.value // Show all bots for students
  }
  if (showLibrary.value) {
    let botsFiltered = bots.value
    if (isFilterWidgetVisible.value) {
      tagCategories.value.forEach(tagCategory => {
        let filterArray = tagCategory.tagItems
          .filter(tagItem => tagItem.checked)
          .map(tagItem => tagItem.weight)
        if (filterArray.length > 0) {
          let binarySum = filterArray.reduce((partialSum, a) => partialSum + Math.pow(2, a), 0)
          botsFiltered = botsFiltered.filter(
            bot =>
              bot.tag.filter(tag => tag.categoryId === tagCategory.id && tag.tagValue & binarySum)
                .length > 0
          )
        }
      })
    }
    return botsFiltered.filter(bot => !bot.personal && !bot.mandatory)
  } else {
    return bots.value.filter(bot => bot.mandatory || bot.personal || bot.favorite)
  }
})

const tagCategoriesSorted = computed(() => {
  return tagCategories.value.sort((a, b) => a.order - b.order)
})

const tagItemSorted = tagCategory => {
  return tagCategory.tagItems.sort((a, b) => a.order - b.order)
}

const botTileBg = bot => {
  if (bot.personal) {
    return 'oslo-bg-light'
  } else {
    return 'oslo-bg-light'
  }
}

const toggleFavorite = async bot => {
  try {
    const { data } = await axios.put('/api/favorite/' + bot.uuid)
    bot.favorite = data.favorite
  } catch (error) {
    console.log(error)
  }
}

const onLoginModalClosed = () => {
  loginUserName.value = ''
  loginUserPassword.value = ''
  showPassword.value = false
}

const setActiveBot = bot => {
  activeBot.value = bot
}

const botIconWidth = computed(() =>
  showLibrary.value && isBotFilteringEnabled.value && isFilterWidgetVisible.value
    ? 'col-xxl-3 col-xl-3 col-lg-4 col-md-6 col-12'
    : 'col-xxl-2 col-xl-2 col-lg-3 col-md-4 col-6'
)

const newLink = computed(() => (showLibrary.value ? 'editbot/newlib' : 'editbot/new'))

const botLink = bot => (bot.imgBot ? 'imgbot/' + bot.uuid : 'bot/' + bot.uuid)

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
  <div
    class="modal fade"
    id="botinfo"
    tabindex="-1"
    aria-labelledby="botInfoLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div v-if="activeBot" class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="botInfoLabel">
            {{ activeBot.botTitle }}
          </h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <span v-html="activeBot.botInfo"></span>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn oslo-btn-secondary" data-bs-dismiss="modal">Lukk</button>
        </div>
      </div>
    </div>
  </div>
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
              <!-- <label for="username" class="form-label">Brukernavn</label> -->
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
      lagrer personopplysninger. Vi tester løsningen skoleårene 2023/2024 og 2024/2025. Les mer
      under "Om tjenesten"
    </p>
    <div v-if="bots.length === 0">
      <div class="card">
        <div class="card-body">
          <h5 class="card-text">Du har ikke fått tilgang til noen boter</h5>
        </div>
      </div>
    </div>

    <!-- bibliotek -->
    <div v-if="store.isEmployee || store.isAdmin">
      <div class="form-check form-switch mb-2">
        <input class="form-check-input" type="checkbox" id="showAll" v-model="showLibrary" />
        <label class="form-check form-check-label" for="showAll">Vis bibliotek</label>
      </div>
      <div v-if="showLibrary && isBotFilteringEnabled" class="form-check form-switch mb-2">
        <input
          class="form-check-input"
          type="checkbox"
          id="showFilter"
          v-model="isFilterWidgetVisible"
        />
        <label class="form-check form-check-label" for="showFilter">Filtrer</label>
      </div>
    </div>

    <div class="row align-items-stretch">
      <div
        v-if="showLibrary && isBotFilteringEnabled && isFilterWidgetVisible"
        class="col-xxl-2 col-lg-3 col-md-3 col-4"
      >
        <div class="card card-body">
          <div v-for="tagCategory in tagCategoriesSorted" :key="tagCategory.id">
            <div>{{ tagCategory.label }}</div>
            <div v-for="tagItem in tagItemSorted(tagCategory)" :key="tagItem.id" class="form-check">
              <input
                class="form-check-input"
                type="checkbox"
                v-model="tagItem.checked"
                :id="`filterCheck${tagCategory.id}:${tagItem.id}`"
              />
              <label class="form-check-label" :for="`filterCheck${tagCategory.id}:${tagItem.id}`">
                {{ tagItem.label }}
              </label>
            </div>
          </div>
        </div>
      </div>
      <div class="col">
        <div class="row">
          <div v-for="bot in filterBots" :key="bot.uuid" :class="botIconWidth" class="mb-3">
            <RouterLink active-class="active" class="bot_tile" :to="botLink(bot)">
              <div class="card text-center h-100" :class="botTileBg(bot)">
                <span v-if="bot.personal" class="visually-hidden">Personlig bot</span>
                <div class="row text-center m-0 pt-3">
                  <div class="col-2"></div>
                  <div class="col-8 p-0">
                    <BotAvatar :avatarScheme="bot.avatarScheme" />
                  </div>

                  <div v-if="store.isEmployee" class="col-2 px-0">
                    <div v-if="bot.mandatory"></div>
                    <div v-if="bot.personal"></div>
                    <div v-if="!bot.mandatory && !bot.personal">
                      <a href="#" @click.prevent="toggleFavorite(bot)">
                        <img
                          v-if="bot.favorite"
                          src="@/components/icons/star_solid.svg"
                          alt="Fjern som favoritt"
                        />
                        <img v-else src="@/components/icons/star.svg" alt="Sett som favoritt" />
                      </a>
                    </div>
                  </div>
                  <div v-if="store.isAdmin" class="col-2 px-0">
                    <span class="badge text-bg-secondary">
                      {{ bot.accessCount }}
                    </span>
                  </div>
                  <div class="card-body row m-0">
                    <div class="col-10 ps-0">{{ bot.botTitle }}</div>
                    <a
                      v-if="bot.botInfo"
                      class="col px-0"
                      href="#"
                      data-bs-toggle="modal"
                      data-bs-target="#botinfo"
                      @click.prevent="setActiveBot(bot)"
                    >
                      <img src="@/components/icons/information.svg" alt="Informasjon" />
                    </a>
                  </div>
                </div>
              </div>
            </RouterLink>
          </div>
          <RouterLink
            v-if="store.isAuthor || store.isAdmin || (store.isEmployee && !showLibrary)"
            active-class="active"
            :class="botIconWidth"
            class="mb-3"
            :to="newLink"
          >
            <div class="card oslo-bg-light text-center h-100">
              <div class="row text-center pt-3">
                <div class="col-2"></div>
                <div class="col-8">
                  <svg viewBox="0 0 12 18">
                    <rect class="oslo-fill-black" x="3" y="8" width="6" height="2" />
                    <rect class="oslo-fill-black" x="5" y="6" width="2" height="6" />
                  </svg>
                </div>
              </div>
              <div class="card-body d-flex flex-column">
                <h5 v-if="showLibrary" class="card-title">Ny biblioteksbot</h5>
                <h5 v-else class="card-title">Ny bot</h5>
              </div>
            </div>
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>
