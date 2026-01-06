<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { axiosInstance as axios } from '../clients'
import { ref, computed, watch, inject } from 'vue'
import { store } from '../store.js'
import BotAvatar from '@/components/BotAvatar.vue'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import { nb } from 'date-fns/locale'
import '@vuepic/vue-datepicker/dist/main.css'

let lastGoType = ''
let dateFormat = Intl.DateTimeFormat('nb', {
  weekday: 'long',
  month: 'long',
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})
const route = useRoute()
const router = useRouter()
const groups = ref([])
const defaultLifeSpan = ref(0)
const maxLifeSpan = ref(0)
const botId = ref()

const bot = inject('bot')

const getGroupInfo = async () => {
  try {
    const { data } = await axios.get('/api/bot_groups/' + route.params.id)
    groups.value = data.groups
    defaultLifeSpan.value = data.defaultLifespan
    maxLifeSpan.value = data.maxLifespan
  } catch (error) {
    console.log(error)
  }
}

const saveDistribution = async () => {
  try {
    await axios.patch('/api/bot_groups/' + route.params.id, {
      groups: groups.value,
    })
    store.addMessage('Endringene er lagret!', 'info')
  } catch (error) {
    console.log(error)
  }
  router.push({ name: 'bot', params: { id: route.params.id } })
}

const isGroupHeading = group => {
  const isNewGroupType = lastGoType !== group.goType
  lastGoType = group.goType
  return isNewGroupType
}

const groupsSorted = computed(() => {
  return groups.value.sort((a, b) => a.displayName.localeCompare(b.displayName))
})

watch(
  route,
  () => {
    getGroupInfo()
  },
  { immediate: true }
)
</script>

<template>
  <div class="d-flex justify-content-end">
    <button @click="saveDistribution" class="btn oslo-btn-primary">Lagre</button>
    <RouterLink class="btn oslo-btn-secondary" :to="{ name: 'bot', params: { id: botId } }">
      Avbryt
    </RouterLink>
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

  <div class="row">
    <div class="col-sm-2"></div>
    <div class="col"></div>
  </div>
  <div class="row mb-3">
    <div class="col-sm-2">Grupper som har tilgang</div>
    <div class="col-sm-8">
      <div v-for="group in groupsSorted" :key="group.id" class="">
        <div v-if="isGroupHeading(group)" class="fw-bold">
          {{ group.goType == 'b' ? 'Klasser' : 'Faggrupper' }}
        </div>
        <div
          v-if="group.checked"
          class="row justify-content-between align-items-center bg-light mb-2 pb-1 pt-1"
        >
          <div class="col-sm-8">
            <div class="form-check form-switch">
              <input
                class="form-check-input"
                type="checkbox"
                role="switch"
                name="access"
                v-model="group.checked"
                :id="'check' + group.id"
              />
              <label class="form-check-label" :for="'check' + group.id">
                {{ group.displayName }}
              </label>
            </div>
            <div class="ps-5">
              Åpen fra
              {{ dateFormat.format(new Date(group.validRange[0])) }}
            </div>
            <div class="ps-5">
              Åpen til
              {{ dateFormat.format(new Date(group.validRange[1])) }}
            </div>
          </div>
          <VueDatePicker
            class="date-picker col"
            v-show="group.checked"
            v-model="group.validRange"
            :range="{
              maxRange: maxLifeSpan,
              partialRange: false,
            }"
            :locale="nb"
            :formats="{
              input: () => {
                return 'Endre tidspunkt'
              },
              preview: 'dd.MM HH:mm',
            }"
            :action-row="{
              selectBtnLabel: 'Velg',
              cancelBtnLabel: 'Avbryt',
            }"
            :input-attrs="{
              clearable: false,
            }"
            :time-config="{
              ignoreTimeValidation: true,
            }"
            :min-date="new Date()"
          />
        </div>
        <div v-else class="form-check form-switch pt-1">
          <input
            class="form-check-input"
            type="checkbox"
            role="switch"
            name="access"
            v-model="group.checked"
            :id="'check' + group.id"
          />
          <label class="form-check-label" :for="'check' + group.id">
            {{ group.displayName }}
          </label>
        </div>
      </div>
    </div>
  </div>

  <div class="d-flex flex-row-reverse mb-3">
    <RouterLink class="btn oslo-btn-secondary" :to="{ name: 'bot', params: { id: botId } }">
      Avbryt
    </RouterLink>
    <button @click="saveDistribution" class="btn oslo-btn-primary">Lagre</button>
  </div>
</template>

<style scoped>
.date-picker {
  width: 180px;
  --dp-background-color: #f8f0dd;
  --dp-border-color: #f8f0dd;
  --dp-border-radius: 0;
}
</style>
