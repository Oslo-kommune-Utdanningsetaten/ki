<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { axiosInstance as axios } from '../clients'
import { ref, computed, watchEffect, watch, inject } from 'vue'
import { store } from '../store.js'
import BotAvatar from '@/components/BotAvatar.vue'
import BotAvatarEditor from '@/components/BotAvatarEditor.vue'
import { defaultAvatarScheme } from '@/utils/botAvatar.js'

var dataLoaded = false
const route = useRoute()
const router = useRouter()
const bot = inject('bot', ref({}))
const models = ref([])
const method = ref('edit')
const botId = ref()
const sortBy = ref('schoolName')
const selectedAccessFilters = ref([])
let accessOptions = []
const accessOptionsAdmin = [
  { value: 'none', label: 'Ingen' },
  { value: 'emp', label: 'Ansatte' },
  { value: 'all', label: 'Alle' },
  { value: 'levels', label: 'Trinn' },
]
const accessOptionsAuthor = [
  { value: 'none', label: 'Ingen' },
  { value: 'emp', label: 'Ansatte' },
]
const levels = [
  { id: 'aarstrinn1', name: '1.' },
  { id: 'aarstrinn2', name: '2.' },
  { id: 'aarstrinn3', name: '3.' },
  { id: 'aarstrinn4', name: '4.' },
  { id: 'aarstrinn5', name: '5.' },
  { id: 'aarstrinn6', name: '6.' },
  { id: 'aarstrinn7', name: '7.' },
  { id: 'aarstrinn8', name: '8.' },
  { id: 'aarstrinn9', name: '9.' },
  { id: 'aarstrinn10', name: '10.' },
  { id: 'vg1', name: 'Vg1' },
  { id: 'vg2', name: 'Vg2' },
  { id: 'vg3', name: 'Vg3' },
]

const setAccessOptions = () => {
  if (store.isAdmin) {
    accessOptions = accessOptionsAdmin
  } else if (store.isAuthor) {
    accessOptions = accessOptionsAuthor
  } else {
    accessOptions = []
  }
}

const initializeCopy = () => {
  bot.value.uuid = null
  bot.value.owner = null
  bot.value.title = 'Kopi av ' + bot.value.title
  bot.value.mandatory = false
  bot.value.allowDistribution = true
  bot.value.isAudioEnabled = false
  bot.value.model = 'none'
  bot.value.edit = true
  bot.value.library = false
  bot.value.botInfo = ''
  bot.value.choices.forEach(choice => {
    choice.id = Math.random().toString(36).substring(7)
    choice.options.forEach(option => {
      option.id = Math.random().toString(36).substring(7)
    })
  })
  bot.value.schoolAccesses = []
}

const initializeNew = (isLibrary = false) => {
  bot.value.uuid = null
  bot.value.owner = null
  bot.value.title = ''
  bot.value.mandatory = false
  bot.value.allowDistribution = true
  bot.value.isAudioEnabled = false
  bot.value.model = 'none'
  bot.value.edit = true
  bot.value.library = isLibrary
  bot.value.avatarScheme = defaultAvatarScheme
  bot.value.botInfo = ''
  bot.value.choices = []
  bot.value.schoolAccesses = []
}

const saveBotData = async () => {
  if (newBot.value) {
    try {
      const { data } = await axios.post('/api/bot_info/', bot.value)
      botId.value = data.bot.uuid
      store.addMessage('Boten er opprettet!', 'info')
    } catch (error) {
      console.log(error)
    }
  } else if (method.value == 'edit') {
    try {
      await axios.put('/api/bot_info/' + botId.value, bot.value)
      store.addMessage('Endringene er lagret!', 'info')
    } catch (error) {
      console.log(error)
    }
  }

  router.push({ name: 'bot', params: { id: botId.value } })
}

const deleteChoice = choice => {
  bot.value.choices = bot.value.choices.filter(c => c.id !== choice.id)
}

const addChoice = () => {
  bot.value.choices.push({
    id: Math.random().toString(36).substring(7),
    label: '',
    text: '',
    options: [],
    selected: false,
    order: Math.max(...bot.value.choices.map(c => c.order), -1) + 1,
  })
}

const notFirstChoice = choice => {
  return choice.order > 0
}

const notLastChoice = choice => {
  return choice.order < bot.value.choices.length - 1
}

const notFirstOption = (_, option) => {
  return option.order > 0
}

const notLastOption = (choice, option) => {
  return option.order < choice.options.length - 1
}

const choiceOrderUp = choice => {
  if (choice.order > 0) {
    const other = bot.value.choices.find(c => c.order === choice.order - 1)
    other.order++
    choice.order--
  }
}

const choiceOrderDown = choice => {
  if (choice.order < bot.value.choices.length - 1) {
    const other = bot.value.choices.find(c => c.order === choice.order + 1)
    other.order--
    choice.order++
  }
}

const optionOrderUp = (choice, option) => {
  if (option.order > 0) {
    const other = choice.options.find(o => o.order === option.order - 1)
    other.order++
    option.order--
  }
}

const optionOrderDown = (choice, option) => {
  if (option.order < choice.options.length - 1) {
    const other = choice.options.find(o => o.order === option.order + 1)
    other.order--
    option.order++
  }
}

const deleteOption = (choice, option) => {
  choice.options = choice.options.filter(o => o.id !== option.id)
}

const addOption = choice => {
  choice.options.push({
    id: Math.random().toString(36).substring(7),
    label: '',
    text: '',
    order: Math.max(...choice.options.map(o => o.order), -1) + 1,
  })
}

const setAllAccesses = access => {
  bot.value.schoolAccesses.forEach(school => {
    school.access = access
  })
}

const choicesSorted = computed(() => {
  if (!bot.value.choices) {
    return []
  }
  return bot.value.choices.sort((a, b) => a.order - b.order)
})

const optionsSorted = choice => {
  return choice.options.sort((a, b) => a.order - b.order)
}

const schoolAccessFiltered = computed(() => {
  let filteredSchoolAccesses = []
  if (selectedAccessFilters.value.length > 0) {
    filteredSchoolAccesses = bot.value.schoolAccesses.filter(school =>
      selectedAccessFilters.value.includes(school.access)
    )
  } else {
    filteredSchoolAccesses = bot.value.schoolAccesses || []
  }

  return filteredSchoolAccesses.sort((a, b) => {
    if (a[sortBy.value] < b[sortBy.value]) {
      return -1
    }
    if (a[sortBy.value] > b[sortBy.value]) {
      return 1
    }
    return 0
  })
})

const groupsSorted = computed(() => {
  return bot.value.groups.sort((a, b) => a.displayName.localeCompare(b.displayName))
})

const updateAvatarScheme = newAvatarScheme => {
  bot.value.avatarScheme = newAvatarScheme
}

const newBot = computed(() => {
  return method.value == 'new' || method.value == 'newlib'
})

watch(
  () => route.fullPath,
  () => {
    const legalMethods = ['edit', 'new', 'newlib', 'copy']
    if (!legalMethods.includes(route.params.method)) {
      router.push('home')
    }
    botId.value = route.params.id
    method.value = route.params.method
    if (newBot.value) {
      initializeNew(method.value == 'newlib')
    } else if (method.value == 'copy') {
      initializeCopy()
    }
    dataLoaded = true
    setAccessOptions()
  },
  { immediate: true }
)
</script>

<template>
  <div>
    <!-- modal -->
    <div
      class="modal fade"
      id="genBotImg"
      tabindex="-1"
      aria-labelledby="genBotImgLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-custom-width">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="genBotImgLabel">Bot avatar</h1>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>

          <BotAvatarEditor
            :avatarScheme="bot.avatarScheme"
            @update:avatarScheme="updateAvatarScheme"
          />

          <div class="modal-footer">
            <button type="button" class="btn oslo-btn-secondary" data-bs-dismiss="modal">
              Lukk
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="d-flex justify-content-end">
      <RouterLink v-if="newBot" class="btn oslo-btn-secondary" :to="{ name: 'home' }">
        Avbryt
      </RouterLink>
      <RouterLink
        v-else
        class="btn oslo-btn-secondary"
        :to="{ name: 'bot', params: { id: botId } }"
      >
        Avbryt
      </RouterLink>
      <button @click="saveBotData" class="btn oslo-btn-primary">Lagre</button>
    </div>
    <div class="row mb-4">
      <div class="col-sm-1">
        <BotAvatar :avatarScheme="bot.avatarScheme" />
      </div>
      <div class="col-sm-1"></div>
      <h1 class="col align-self-center h2">
        {{ bot.title }}
      </h1>
    </div>
    <div class="row mb-3">
      <label for="botTitle" class="col-sm-2 col-form-label">Tittel på boten</label>
      <div class="col-sm-10">
        <input
          v-model="bot.title"
          type="text"
          class="form-control"
          id="botTitle"
          name="title"
          maxlength="40"
        />
        <div class="form-text text-end">{{ bot.title.length }}/40</div>
      </div>
    </div>
    <div class="row mb-3">
      <label for="botIngress" class="col-sm-2 col-form-label">Ingress</label>
      <div class="col-sm-10">
        <input
          v-model="bot.ingress"
          type="text"
          class="form-control"
          id="botIngress"
          name="ingress"
        />
      </div>
    </div>
    <div class="row mb-3">
      <label for="botPromt" class="col-sm-2 col-form-label">Ledetekst</label>
      <div class="col-sm-10">
        <textarea
          v-model="bot.prompt"
          class="form-control"
          id="botPromt"
          rows="5"
          name="prompt"
        ></textarea>
      </div>
    </div>
    <div class="row mb-3">
      <label for="promptVisibility" class="col-sm-2 col-form-label">Ledetekst synlig</label>
      <div class="col-sm-10">
        <div class="form-check form-switch">
          <input
            class="form-check-input"
            type="checkbox"
            role="switch"
            id="promptVisibility"
            v-model="bot.promptVisibility"
          />
        </div>
      </div>
    </div>
    <div class="row mb-3">
      <div class="col-sm-2 col-form-label">Utseende på bot</div>
      <div class="col">
        <button
          class="btn oslo-btn-secondary ms-0"
          data-bs-toggle="modal"
          data-bs-target="#genBotImg"
        >
          Endre
        </button>
      </div>
    </div>
    <div class="row mb-3">
      <label for="temperature" class="col-sm-2 col-form-label">Temperatur</label>
      <div class="col-sm-1">
        <input
          type="range"
          class="form-range"
          min="0.5"
          max="1.5"
          step="0.1"
          id="temperature"
          v-model="bot.temperature"
        />
      </div>
      <div class="col-sm-1">
        {{ bot.temperature * 10 - 5 }}
      </div>
      <div class="col">
        Temperatur er et mål på hvor kreativ boten skal være. Høy temperatur gir mer kreative svar.
      </div>
    </div>

    <div v-if="store.isAdmin" class="row mb-3">
      <label for="mandatory" class="col-sm-2 col-form-label">Tvungen visning</label>
      <div class="col-sm-10">
        <div class="form-check form-switch">
          <input
            class="form-check-input"
            type="checkbox"
            role="switch"
            id="mandatory"
            v-model="bot.mandatory"
          />
        </div>
      </div>
    </div>
    <div v-if="store.isAdmin" class="row mb-3">
      <label for="botOwner" class="col-sm-2 col-form-label">Eier</label>
      <div class="col-sm-10">
        <input v-model="bot.owner" type="text" class="form-control" id="botOwner" name="owner" />
      </div>
    </div>
    <div v-if="store.isAdmin" class="row mb-3">
      <label for="library" class="col-sm-2 col-form-label">Biblioteksbot</label>
      <div class="col-sm-10">
        <div class="form-check form-switch">
          <input
            class="form-check-input"
            type="checkbox"
            role="switch"
            id="library"
            v-model="bot.library"
          />
        </div>
      </div>
    </div>
    <div v-if="store.isAdmin || store.isAudioModifiableByEmployees" class="row mb-3">
      <label for="isAudioEnabled" class="col-sm-2 col-form-label">Kan bruke tale</label>
      <div class="col-sm-10">
        <div class="form-check form-switch">
          <input
            class="form-check-input"
            type="checkbox"
            role="switch"
            id="isAudioEnabled"
            v-model="bot.isAudioEnabled"
          />
        </div>
      </div>
    </div>
    <fieldset v-if="store.isAdmin || (store.isAuthor && bot.library)">
      <div class="row mb-3">
        <legend class="col-sm-2 col-form-label">Modell</legend>
        <div class="col-sm-10">
          <div
            v-for="modelItem in models"
            :key="modelItem.modelId"
            class="form-check form-check-inline"
          >
            <input
              class="form-check-input"
              type="radio"
              :id="'m' + modelItem.modelId"
              :value="modelItem"
              v-model="bot.model"
            />
            <label class="form-check-label" :for="'m' + modelItem.modelId">
              {{ modelItem.displayName }}
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input
              class="form-check-input"
              type="radio"
              id="no_model"
              value="none"
              v-model="bot.model"
            />
            <label class="form-check-label" for="no_model">Sentralt satt</label>
          </div>
        </div>
      </div>
      <div v-if="bot.model" class="row mb-3">
        <div class="col-sm-2"></div>
        <div class="col-sm-10">
          {{ bot.model.modelDescription }}
        </div>
      </div>
    </fieldset>
    <div v-if="store.isAdmin || (store.isAuthor && bot.library)" class="row mb-3">
      <label for="allowDistribution" class="col-sm-2 col-form-label">
        Tillat distribusjon til elever
      </label>
      <div class="col-sm-10">
        <div class="form-check form-switch">
          <input
            class="form-check-input"
            type="checkbox"
            role="switch"
            id="allowDistribution"
            v-model="bot.allowDistribution"
          />
        </div>
      </div>
    </div>
    <div v-if="store.isAdmin || (store.isAuthor && bot.library)" class="row mb-3">
      <label for="botInfo" class="col-sm-2 col-form-label">Informasjon (vises på startsiden)</label>
      <div class="col-sm-10">
        <textarea
          v-model="bot.botInfo"
          class="form-control"
          id="botInfo"
          rows="5"
          name="botInfo"
        ></textarea>
      </div>
    </div>
    <div v-if="store.isAdmin || (store.isAuthor && bot.library)" class="row mb-3">
      <div class="col-sm-2">Filtertag for</div>
      <div class="col-sm-10">
        <div v-for="tagCategory in bot.tagCategories" :key="tagCategory.id">
          <div>{{ tagCategory.label }}</div>
          <div v-for="tag in tagCategory.tags" :key="tag.id" class="form-check form-check-inline">
            <input
              class="form-check-input"
              type="checkbox"
              v-model="tag.checked"
              :id="`filterCheck${tagCategory.id}:${tag.id}`"
            />
            <label class="form-check-label" :for="`filterCheck${tagCategory.id}:${tag.id}`">
              {{ tag.label }}
            </label>
          </div>
        </div>
      </div>
    </div>

    <div class="mb-3">
      <button
        class="btn oslo-btn-primary ms-0"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#collapseAdvanced"
        aria-expanded="false"
        aria-controls="collapseAdvanced"
      >
        Avanserte innstillinger
      </button>
    </div>
    <div class="mb-3">
      <div class="collapse" id="collapseAdvanced">
        <div class="row mb-3">
          <div class="col-sm-2">Forhåndsvalg</div>
          <div class="col-sm-10">
            <div v-for="choice in choicesSorted" class="card mb-3 p-3">
              <div class="row mb-1">
                <label :for="`choiceLabel${choice.id}`" class="col-sm-2 col-form-label">
                  Spørsmål
                </label>
                <div class="col-sm-10">
                  <input
                    type="text"
                    class="form-control"
                    :id="`choiceLabel${choice.id}`"
                    v-model="choice.label"
                    maxlength="50"
                  />
                  <div class="form-text text-end">{{ choice.label.length }}/50</div>
                </div>
              </div>
              <div class="row mb-1">
                <div class="col-sm-2">Alternativer</div>
                <div class="col-sm-10">
                  <div v-for="option in optionsSorted(choice)">
                    <div class="row mb-1">
                      <label :for="`optLabel{option.id}`" class="col-sm-2 col-form-label">
                        Knapp
                      </label>
                      <div class="col-sm-10">
                        <input
                          type="text"
                          class="form-control"
                          :id="`optLabel{option.id}`"
                          v-model="option.label"
                          maxlength="50"
                        />
                        <div class="form-text text-end">{{ option.label.length }}/50</div>
                      </div>
                    </div>
                    <div class="row mb-1">
                      <label :for="`optText{option.id}`" class="col-sm-2 col-form-label">
                        Ledetekst
                      </label>
                      <div class="col-sm-10">
                        <textarea
                          class="form-control"
                          :id="`optText{option.id}`"
                          rows="1"
                          v-model="option.text"
                        ></textarea>
                      </div>
                    </div>
                    <input
                      class="btn-check"
                      type="radio"
                      :id="`${choice.id}-${option.id}`"
                      :value="option"
                      v-model="choice.selected"
                    />
                    <label class="btn oslo-btn-secondary" :for="`${choice.id}-${option.id}`">
                      Valgt
                    </label>
                    <button class="btn oslo-btn-warning" @click="deleteOption(choice, option)">
                      Slett alternativ
                    </button>
                    <button
                      v-if="notFirstOption(choice, option)"
                      class="btn oslo-btn-secondary"
                      @click="optionOrderUp(choice, option)"
                    >
                      <img src="@/components/icons/move_up.svg" alt="flytt opp" />
                    </button>
                    <button
                      v-if="notLastOption(choice, option)"
                      class="btn oslo-btn-secondary"
                      @click="optionOrderDown(choice, option)"
                    >
                      <img src="@/components/icons/move_down.svg" alt="flytt ned" />
                    </button>
                    <!-- {{ option.order }} -->
                    <hr />
                  </div>
                  <button class="btn oslo-btn-primary" @click="addOption(choice)">
                    Legg til alternativ
                  </button>
                </div>
              </div>
              <div class="mb-1">
                <button class="btn oslo-btn-warning" @click="deleteChoice(choice)">
                  Slett spørsmål
                </button>
                <button
                  v-if="notFirstChoice(choice)"
                  class="btn oslo-btn-secondary"
                  @click="choiceOrderUp(choice)"
                >
                  <img src="@/components/icons/move_up.svg" alt="flytt opp" />
                </button>
                <button
                  v-if="notLastChoice(choice)"
                  class="btn oslo-btn-secondary"
                  @click="choiceOrderDown(choice)"
                >
                  <img src="@/components/icons/move_down.svg" alt="flytt ned" />
                </button>
                <!-- {{ choice.order }} -->
              </div>
            </div>
            <div class="mb-1">
              <button class="btn oslo-btn-primary" @click="addChoice">Legg til spørsmål</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="d-flex justify-content-end">
      <RouterLink v-if="newBot" class="btn oslo-btn-secondary" :to="{ name: 'home' }">
        Avbryt
      </RouterLink>
      <RouterLink
        v-else
        class="btn oslo-btn-secondary"
        :to="{ name: 'bot', params: { id: botId } }"
      >
        Avbryt
      </RouterLink>
      <button @click="saveBotData" class="btn oslo-btn-primary">Lagre</button>
    </div>

    <div v-if="store.isAdmin || (store.isAuthor && bot.library)" class="mb-3">
      <hr />
      <div class="row mb-3">
        <div class="col-sm-2">Tilgang</div>
        <div class="card col mb-3 p-3">
          <ul class="list-group list-group-flush">
            <li v-if="store.isAdmin" class="list-group-item">
              <div class="row">
                <div class="col-4">Sett alle skoler til:</div>
                <div v-for="option in accessOptions" :key="option.value" class="e col-1">
                  <button class="btn oslo-btn-secondary" @click="setAllAccesses(option.value)">
                    {{ option.label }}
                  </button>
                </div>
              </div>
              <div class="row">
                <div class="col-4">Filtrer på tilgang:</div>
                <div
                  v-for="option in accessOptions"
                  :key="option.value"
                  class="form-check form-check-inline col-1"
                >
                  <input
                    class="form-check-input"
                    :id="'filter' + option.value"
                    :value="option.value"
                    type="checkbox"
                    v-model="selectedAccessFilters"
                  />
                  <label class="form-check-label" :for="'filter' + option.value">
                    {{ option.label }}
                  </label>
                </div>
              </div>
            </li>
            <li v-for="school in schoolAccessFiltered" class="list-group-item">
              <div class="row">
                <div class="col-4">
                  {{ school.schoolName }}
                </div>
                <div
                  v-for="option in accessOptions"
                  :key="option.value"
                  class="form-check form-check-inline col-1"
                >
                  <input
                    class="form-check-input"
                    :id="school.orgNr + option.value"
                    :value="option.value"
                    type="radio"
                    v-model="school.access"
                  />
                  <label class="form-check-label" :for="option.value">{{ option.label }}</label>
                </div>
              </div>
              <div v-if="school.access == 'levels'" class="row">
                <div class="col-2">Trinn:</div>
                <div class="col">
                  <span v-for="level in levels" class="form-check form-check-inline">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      :id="'level' + school.orgNr + level.id"
                      :value="level.id"
                      v-model="school.accessList"
                    />
                    <label class="form-check-label" :for="'level' + school.orgNr + level.id">
                      {{ level.name }}
                    </label>
                  </span>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <div class="d-flex justify-content-end">
        <RouterLink v-if="newBot" class="btn oslo-btn-secondary" :to="{ name: 'home' }">
          Avbryt
        </RouterLink>
        <RouterLink
          v-else
          class="btn oslo-btn-secondary"
          :to="{ name: 'bot', params: { id: botId } }"
        >
          Avbryt
        </RouterLink>
        <button @click="saveBotData" class="btn oslo-btn-primary">Lagre</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-custom-width {
  width: 600px;
  max-width: none;
}
</style>
