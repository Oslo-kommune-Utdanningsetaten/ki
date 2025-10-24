<script setup>
import { useRoute } from 'vue-router'
import { axiosInstance as axios } from '../clients'
import { ref, onMounted, computed } from 'vue'

const route = useRoute()
const settings = ref([])

onMounted(async () => {
  await getSettings()
})

const getSettings = async () => {
  try {
    const { data } = await axios.get('/api/settings')
    settings.value = data.settings
  } catch (error) {
    console.log(error)
  }
}

const settingsChange = async setting => {
  try {
    const { data } = await axios.put('/api/settings', { setting })
  } catch (error) {
    console.log(error)
  }
}
</script>

<template>
  <div class="card">
    <div class="card-body">
      <h3 class="h4">Globale innstillinger</h3>
      <div v-for="setting in settings" class="form-group row">
        <label :for="setting.settingKey" class="col-sm-3 col-form-label">
          {{ setting.label }}
        </label>
        <div class="col-sm-3">
          <input
            :type="setting.type"
            :id="setting.settingKey"
            class="form-control"
            v-model="setting.value"
            maxlength="50"
            @change="settingsChange(setting)"
          />
        </div>
      </div>
    </div>
  </div>
</template>
