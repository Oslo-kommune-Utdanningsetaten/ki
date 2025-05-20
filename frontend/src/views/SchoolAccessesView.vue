<script setup>
import { useRoute } from 'vue-router'
import { axiosInstance as axios } from '../clients'
import { ref, onMounted, computed } from 'vue'

const route = useRoute()
const schoolAccess = ref([])
const filter_list = ref([])
const access_options = [
  { value: 'none', label: 'Ingen' },
  { value: 'emp', label: 'Ansatte' },
  { value: 'all', label: 'Alle' },
  { value: 'levels', label: 'Trinn' },
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

onMounted(async () => {
  await getSchoolAccess()
})

const getSchoolAccess = async () => {
  try {
    const { data } = await axios.get('/api/school_access')
    schoolAccess.value = data.schools
  } catch (error) {
    console.log(error)
  }
}

const schoolAccessChange = async school => {
  try {
    const { data } = await axios.put('/api/school_access', { school })
    // schoolAccess.value = data.schools;
  } catch (error) {
    console.log(error)
  }
}

const schoolAccessFiltered = computed(() => {
  if (filter_list.value.length > 0) {
    return schoolAccess.value.filter(school => filter_list.value.includes(school.access))
  }
  return schoolAccess.value
})
</script>

<template>
  <div class="card mt-3">
    <div class="card-body">
      <h3 class="h4">Skoletilgang</h3>
      <ul class="list-group">
        <li class="list-group-item">
          <div class="row">
            <div class="col-4">Filter (viser {{ schoolAccessFiltered.length }} skoler)</div>
            <div
              v-for="option in access_options"
              :key="option.value"
              class="form-check form-check-inline col-1"
            >
              <input
                class="form-check-input"
                :id="'filter' + option.value"
                :value="option.value"
                type="checkbox"
                v-model="filter_list"
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
              {{ school.school_name }}
            </div>
            <div
              v-for="option in access_options"
              :key="option.value"
              class="form-check form-check-inline col-1"
            >
              <input
                class="form-check-input"
                :id="school.org_nr + option.value"
                :value="option.value"
                type="radio"
                v-model="school.access"
                @change="schoolAccessChange(school)"
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
                  :id="'level' + school.org_nr + level.id"
                  :value="level.id"
                  v-model="school.access_list"
                  @change="schoolAccessChange(school)"
                />
                <label class="form-check-label" :for="'level' + school.org_nr + level.id">
                  {{ level.name }}
                </label>
              </span>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>
