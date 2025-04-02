<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { axiosInstance as axios } from '../clients'
import { ref, computed, watchEffect, watch } from 'vue'
import { store } from '../store.js'
import BotAvatar from '@/components/BotAvatar.vue'
import { defaultAvatarScheme } from '@/utils/botAvatar.js'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

let last_go_type = ''
let dateFormat = Intl.DateTimeFormat('nb', {
  weekday: 'long',
  month: 'long',
  day: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
})
const route = useRoute()
const router = useRouter()
const bot = ref({
  title: '',
  ingress: '',
  prompt: '',
  prompt_visibility: false,
  avatar_scheme: defaultAvatarScheme,
  temperature: 1,
  model: null,
  mandatory: false,
  allow_distribution: false,
  bot_info: '',
  tag_categories: [],
  choices: [],
  schoolAccesses: [],
  groups: [],
  library: false,
})
const defaultLifeSpan = ref(0)
const maxLifeSpan = ref(0)
const botId = ref()

const getBotInfo = async () => {
  var url = '/api/bot_info/' + botId.value
  try {
    const { data } = await axios.get(url)
    bot.value = data.bot
    defaultLifeSpan.value = data.default_lifespan
    maxLifeSpan.value = data.max_lifespan
  } catch (error) {
    console.log(error)
  }
}

const update = async () => {
  try {
    await axios.patch('/api/bot_info/' + botId.value, {
      groups: bot.value.groups,
    })
    store.addMessage('Endringene er lagret!', 'info')
  } catch (error) {
    console.log(error)
  }
  router.push('/bot/' + botId.value)
}

const is_group_heading = group => {
  if (last_go_type == group.go_type) {
    return false
  }
  last_go_type = group.go_type
  return true
}

const groupsSorted = computed(() => {
  return bot.value.groups.sort((a, b) => a.display_name.localeCompare(b.display_name))
})

watch(
  route,
  () => {
    botId.value = route.params.id
    getBotInfo()
  },
  { immediate: true }
)
</script>

<template>
  
  <div class="d-flex justify-content-end">
    <button @click="update" class="btn oslo-btn-primary">Lagre</button>
    <RouterLink class="btn oslo-btn-secondary" :to="bot.uuid ? '/bot/' + bot.uuid : '/'">
      Avbryt
    </RouterLink>  
  </div>
  
  <div class="row mb-4">
    <div class="col-sm-1">
      <BotAvatar :avatar_scheme="bot.avatar_scheme" />
    </div>
    <div class="col-sm-1"></div>
      <h1 class="col align-self-center h2">
      {{ bot.title }}
      </h1>
  </div>  

  <div class="row">
    <div class="col-sm-2"></div>
    <div class="col">
    </div>
  </div>
  <div class="row mb-3">
    <div class="col-sm-2">Grupper som har tilgang</div>
    <div class="col-sm-8">
      <div v-for="group in groupsSorted" :key="group.id" class="">
        <div v-if="is_group_heading(group)" class="fw-bold">
          {{ group.go_type == 'b' ? 'Klasser' : 'Faggrupper' }}
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
                {{ group.display_name }}
              </label>
            </div>
            <div class="ps-5">
              Åpen fra
              {{ dateFormat.format(new Date(group.valid_range[0])) }}
            </div>
            <div class="ps-5">
              Åpen til
              {{ dateFormat.format(new Date(group.valid_range[1])) }}
            </div>
          </div>
          <div class="col">
            <VueDatePicker
              class="date-picker"
              v-show="group.checked"
              v-model="group.valid_range"
              :range="{
                maxRange: maxLifeSpan,
                partialRange: false,
              }"
              locale="nb"
              :format="
                dates => {
                  return 'Endre tidspunkt'
                }
              "
              select-text="Velg"
              cancel-text="Avbryt"
              :clearable="false"
              :min-date="new Date()"
              preview-format="dd.MM HH:mm"
            ></VueDatePicker>
          </div>
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
            {{ group.display_name }}
          </label>
        </div>
      </div>
    </div>
  </div>

  <div class="d-flex flex-row-reverse mb-3">
    <RouterLink
      active-class="active"
      class="btn oslo-btn-secondary"
      :to="bot.uuid ? '/bot/' + bot.uuid : '/'"
    >
      Avbryt
    </RouterLink>
    <button @click="update" class="btn oslo-btn-primary">Lagre</button>
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
