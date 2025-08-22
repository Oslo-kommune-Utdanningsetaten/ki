<script setup>
import { useRoute } from 'vue-router'
import { axiosInstance as axios } from '../clients'
import { ref, onMounted, computed } from 'vue'

const route = useRoute()
const authors = ref([])
const activeAuthor = ref(null)
const schools = ref([])
const newAuthor = ref(false)

onMounted(async () => {
  await getSchools()
  await getAuthors()
})

const getSchools = async () => {
  try {
    const { data } = await axios.get('/api/school_list')
    schools.value = data.schools
  } catch (error) {
    console.log(error)
  }
}

const getAuthors = async () => {
  try {
    const { data } = await axios.get('/api/authors')
    authors.value = data.authors
  } catch (error) {
    console.log(error)
  }
}

const saveAuthor = async author => {
  if (newAuthor.value) {
    try {
      const { data } = await axios.post('/api/author/', {
        author: author,
      })
    } catch (error) {
      console.log(error)
    }
  } else {
    try {
      await axios.put('/api/author/' + author.id, {
        author: author,
      })
    } catch (error) {
      console.log(error)
    }
  }
  activeAuthor.value = null
  newAuthor.value = false
  getAuthors()
}

const deleteAuthor = async author => {
  try {
    await axios.delete('/api/author/' + author.id)
  } catch (error) {
    console.log(error)
  }
  activeAuthor.value = null
  newAuthor.value = false
  getAuthors()
}

const setActiveAuthor = author => {
  activeAuthor.value = author
  newAuthor.value = false
}

const addAuthor = () => {
  activeAuthor.value = {
    name: '',
    username: '',
    school: '',
  }
  newAuthor.value = true
}

const schoolName = schoolId => {
  const school = schools.value.find(s => s.orgNr === schoolId)
  return school ? school.schoolName : ''
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
          <label for="name" class="form-label mt-2">Navn</label>
          <input type="text" class="form-control" id="name" v-model="activeAuthor.name" />
          <label for="userId" class="form-label mt-2">Bruker ID</label>
          <input type="text" class="form-control" id="username" v-model="activeAuthor.username" />
          <div class="form-check mt-2">
            <input
              type="checkbox"
              class="form-check-input"
              id="isExternal"
              v-model="activeAuthor.isExternal"
            />
            <label class="form-check-label" for="isExternal">Ekstern bruker</label>
          </div>
          <label for="school" class="form-label mt-2">Skole</label>
          <select class="form-select" id="school" v-model="activeAuthor.schoolId">
            <option v-for="school in schools" :key="school.orgNr" :value="school.orgNr">
              {{ school.schoolName }}
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
            <div class="col-2">{{ author.username }}</div>
            <div class="col-4">{{ schoolName(author.schoolId) }}</div>
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
