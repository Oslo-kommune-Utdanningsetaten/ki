<script setup>
import { useRoute } from 'vue-router'
import { axiosInstance as axios } from '../clients'
import { ref, onMounted, computed } from 'vue'

const route = useRoute()
const authors = ref([])
const activeAuthor = ref(null)
const schools = ref([])

onMounted(async () => {
  await getSchools()
  await getAutors()
})

const getSchools = async () => {
  try {
    const { data } = await axios.get('/api/school_list')
    schools.value = data.schools
  } catch (error) {
    console.log(error)
  }
}

const getAutors = async () => {
  try {
    const { data } = await axios.get('/api/authors')
    authors.value = data.authors
  } catch (error) {
    console.log(error)
  }
}

const saveAuthor = async author => {
  try {
    const { data } = await axios.put('/api/authors', { author })
    authors.value = data.authors
  } catch (error) {
    console.log(error)
  }
}

const deleteAuthor = async author => {
  try {
    const { data } = await axios.delete('/api/authors', { data: { author } })
    authors.value = data.authors
  } catch (error) {
    console.log(error)
  }
}

const setActiveAuthor = author => {
  activeAuthor.value = author
}

const addAuthor = () => {
  activeAuthor.value = {
    name: '',
    user_id: '',
    school: '',
  }
}

const schoolName = schoolId => {
  const school = schools.value.find(s => s.org_nr === schoolId)
  return school ? school.school_name : ''
}
</script>

<template>
  <!-- modal -->
  <div
    class="modal fade"
    id="editAuthor"
    tabindex="-1"
    aria-labelledby="editAuthorLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="editAuthorLabel">Forfatter</h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>

        <div v-if="activeAuthor" class="modal-body">
          <label for="name" class="form-label">Navn</label>
          <input type="text" class="form-control" id="name" v-model="activeAuthor.name" />
          <label for="user_id" class="form-label">Bruker ID</label>
          <input type="text" class="form-control" id="user_id" v-model="activeAuthor.user_id" />
          <label for="school" class="form-label">Skole</label>
          <select class="form-select" id="school" v-model="activeAuthor.school_id">
            <option v-for="school in schools" :key="school.org_nr" :value="school.org_nr">
              {{ school.school_name }}
            </option>
          </select>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn oslo-btn-primary"
            data-bs-dismiss="modal"
            @click="saveAuthor(activeAuthor)"
          >
            Lagre
          </button>
          <button type="button" class="btn oslo-btn-secondary" data-bs-dismiss="modal">Lukk</button>
        </div>
      </div>
    </div>
  </div>

  <!-- modal -->
  <div
    class="modal fade"
    id="deleteAuthorConfirm"
    tabindex="-1"
    aria-labelledby="deleteAuthorConfirmLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="deleteAuthorConfirmLabel">Forfatter</h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div v-if="activeAuthor" class="modal-body">
          Vil du virkelig slette {{ activeAuthor.name }}?
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn oslo-btn-warning"
            data-bs-dismiss="modal"
            @click="deleteAuthor(activeAuthor)"
          >
            Slett
          </button>
          <button type="button" class="btn oslo-btn-secondary" data-bs-dismiss="modal">Lukk</button>
        </div>
      </div>
    </div>
  </div>

  <div class="card mt-3">
    <div class="card-body">
      <h3 class="h4">Forfattere</h3>
      <ul class="list-group mb-2">
        <li v-for="author in authors" class="list-group-item">
          <div class="row">
            <div class="col-4">{{ author.name }}</div>
            <div class="col-2">{{ author.user_id }}</div>
            <div class="col-4">{{ schoolName(author.school_id) }}</div>
            <div class="col-2">
              <button
                type="button"
                class="btn oslo-btn-secondary"
                data-bs-toggle="modal"
                data-bs-target="#editAuthor"
                @click="setActiveAuthor(author)"
              >
                Endre
              </button>
              <button
                type="button"
                class="btn oslo-btn-warning"
                data-bs-toggle="modal"
                data-bs-target="#deleteAuthorConfirm"
                @click="setActiveAuthor(author)"
              >
                Slett
              </button>
            </div>
          </div>
        </li>
      </ul>
      <button
        class="btn oslo-btn-secondary ms-0"
        data-bs-toggle="modal"
        data-bs-target="#editAuthor"
        @click="addAuthor"
      >
        Legg til forfatter
      </button>
    </div>
  </div>
</template>
