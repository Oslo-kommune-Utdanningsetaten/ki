<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { ref, onMounted } from 'vue'
import BotAvatar from '@/components/BotAvatar.vue'
import BotCommunicationText from '@/components/BotCommunicationText.vue'
import BotCommunicationAudio from '@/components/BotCommunicationAudio.vue'
import { getBot, deleteBot } from '../utils/httpTools.js'

const route = useRoute()
const router = useRouter()
const bot = ref({})
const showSystemPrompt = ref(false)
const communicationMode = ref('audio') // text, audio, maybe video?
const systemPrompt = ref('')

const choicesSorted = () => {
  return bot.value.choices.sort((a, b) => a.order - b.order)
}

const optionsSorted = choice => {
  return choice.options.sort((a, b) => a.order - b.order)
}

const updateSystemPrompt = () => {
  systemPrompt.value = getSystemPrompt()
}

const getSystemPrompt = () => {
  let fullChoicesText = ''
  if (bot.value.choices) {
    choicesSorted().forEach(choice => {
      if (choice.selected !== null) {
        fullChoicesText += choice.selected.text + ' '
      }
    })
  }
  return bot.value.prompt + ' ' + fullChoicesText
}

const toggleStartPrompt = () => {
  showSystemPrompt.value = !showSystemPrompt.value
}

const handleDeleteBot = async botId => {
  await deleteBot(botId)
  router.push({ name: 'home' })
}

const handleSwitchCommunicationMode = () => {
  if (communicationMode.value === 'text') {
    communicationMode.value = 'audio'
  } else {
    communicationMode.value = 'text'
  }
}

onMounted(async () => {
  bot.value = await getBot(route.params.id)
  updateSystemPrompt()
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
            @click="() => handleDeleteBot(bot.uuid)"
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
      {{ bot.title || 'Navnløs chatbot :/' }}
      <button
        v-if="bot.prompt_visibility"
        class="btn oslo-btn-secondary ms-0 me-auto ps-1 pe-1 pt-0 pb-0"
        @click="toggleStartPrompt"
        :class="{ 'oslo-btn-secondary-checked': showSystemPrompt }"
      >
        {{ showSystemPrompt ? 'Skjul' : 'Vis' }} info
      </button>

      <span class="ms-3">
        <input
          type="radio"
          class="btn-check"
          value="text"
          v-model="communicationMode"
          id="communicationModeText"
          autocomplete="off"
        />
        <label
          class="ms-2 me-auto ps-1 pe-1 pt-0 pb-0 btn oslo-btn-secondary"
          for="communicationModeText"
        >
          Skrive
        </label>

        <input
          type="radio"
          class="btn-check"
          value="audio"
          v-model="communicationMode"
          id="communicationModeAudio"
          autocomplete="off"
        />
        <label
          class="ms-0 me-auto ps-1 pe-1 pt-0 pb-0 btn oslo-btn-secondary"
          for="communicationModeAudio"
        >
          Snakke
        </label>
      </span>
    </h1>
    <p v-if="bot.ingress">
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
              @change="updateSystemPrompt()"
            />
            <label class="btn oslo-btn-secondary" :for="`${choice.id}-${option.id}`">
              {{ option.label }}
            </label>
          </span>
        </div>
      </div>
    </div>

    <!-- Show bot info-->
    <div v-if="showSystemPrompt" class="d-flex justify-content-start align-items-end mt-3 mb-2">
      <div class="avatar p-2 me-3">
        <BotAvatar :avatar_scheme="bot.avatar_scheme" />
      </div>
      <div class="speech-bubble-assistant position-relative bg-light p-3 border text-right">
        <strong>Dette er instruksene jeg har fått</strong>
        <p>{{ getSystemPrompt() }}</p>
        <p class="mb-0">
          <strong>Jeg bruker modellen {{ bot.model }}.</strong>
        </p>
      </div>
    </div>
  </div>

  <BotCommunicationText
    v-if="bot.uuid && communicationMode === 'text'"
    :bot="bot"
    :systemPrompt="systemPrompt"
  />
  <BotCommunicationAudio
    v-if="bot.uuid && communicationMode === 'audio'"
    :bot="bot"
    :systemPrompt="systemPrompt"
  />
</template>
