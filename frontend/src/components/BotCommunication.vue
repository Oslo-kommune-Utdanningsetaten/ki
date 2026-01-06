<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { ref, computed, inject } from 'vue'
import BotAvatar from '@/components/BotAvatar.vue'
import BotCommunicationText from '@/components/BotCommunicationText.vue'
import BotCommunicationAudio from '@/components/BotCommunicationAudio.vue'
import { deleteBot } from '@/utils/httpTools.js'
import { store } from '@/store.js'

const router = useRouter()
const showSystemPrompt = ref(false)
const communicationMode = ref('text') // text, audio, maybe video?
const systemPrompt = ref('')
const bot = inject('bot')

const edit = computed(() => {
  return store.isAdmin || (store.isEmployee && bot.value.isOwner)
})

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

const handleDeleteBot = async () => {
  await deleteBot(bot.value.uuid)
  router.push({ name: 'home' })
}

const model = computed(() => {
  if (bot.value.model) {
    return bot.value.model
  } else {
    return store.defaultModel
  }
})
</script>

<template>
  <!-- Modal -->
  <div
    class="modal fade"
    id="deleteBot"
    tabindex="-1"
    aria-labelledby="deleteBotLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="deleteBotLabel">Slette bot</h1>
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
            @click="() => handleDeleteBot()"
          >
            Ja jeg vil slette
          </button>
        </div>
      </div>
    </div>
  </div>

  <div v-if="store.isEmployee || store.isAdmin" class="d-flex justify-content-end">
    <RouterLink
      class="btn oslo-btn-secondary"
      :to="{ name: 'editbot', params: { method: 'copy', id: bot.uuid } }"
    >
      Kopier bot
    </RouterLink>
    <RouterLink
      v-if="bot.isDistributionEnabled"
      class="btn oslo-btn-secondary"
      :to="{ name: 'distribute', params: { id: bot.uuid } }"
    >
      Gi tilgang
    </RouterLink>
    <RouterLink
      v-if="edit"
      class="btn oslo-btn-secondary"
      :to="{ name: 'editbot', params: { method: 'edit', id: bot.uuid } }"
    >
      Rediger bot
    </RouterLink>
    <button
      v-if="edit"
      class="btn oslo-btn-warning"
      data-bs-toggle="modal"
      data-bs-target="#deleteBot"
    >
      Slett bot
    </button>
  </div>

  <div class="p-1">
    <h1 class="h2 mb-3">
      {{ bot.title || 'Navnløs chatbot' }}
      <button
        v-if="bot.promptVisibility || store.isAdmin || store.isEmployee"
        class="btn oslo-btn-secondary ms-3 me-auto ps-1 pe-1 pt-0 pb-0"
        @click="toggleStartPrompt"
        :class="{ 'oslo-btn-secondary-checked': showSystemPrompt }"
      >
        {{ showSystemPrompt ? 'Skjul' : 'Vis' }} bot info
        {{ bot.promptVisibility ? '' : '(kun ansatte)' }}
      </button>

      <span class="ms-3" v-if="bot.isAudioEnabled">
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
        <BotAvatar :avatarScheme="bot.avatarScheme" />
      </div>
      <div class="speech-bubble-assistant position-relative bg-light p-3 border text-right">
        <strong>Dette er instruksene jeg har fått</strong>
        <p>{{ getSystemPrompt() }}</p>
        <strong>Jeg bruker modellen</strong>
        <p>{{ model.displayName }}</p>
        <span v-if="model.trainingCutoff">
          <strong>Jeg er trent på data fram til</strong>
          <p>{{ model.trainingCutoff }}</p>
        </span>
      </div>
    </div>
  </div>

  <BotCommunicationText
    v-if="communicationMode === 'text'"
    :bot="bot"
    :systemPrompt="systemPrompt"
  />
  <BotCommunicationAudio
    v-if="communicationMode === 'audio'"
    :bot="bot"
    :systemPrompt="systemPrompt"
  />
  <!-- </div> -->
</template>
