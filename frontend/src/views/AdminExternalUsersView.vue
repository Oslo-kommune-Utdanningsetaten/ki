<script setup>
import { useRoute } from 'vue-router'
import { store } from '../store.js'
import { axiosInstance as axios } from '../clients.js'
import { ref, onMounted, computed } from 'vue'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

const route = useRoute()
const externalUsers = ref([])
const activeExternalUser = ref(null)
const showPassword = ref(false)

// const schools = ref([])

onMounted(async () => {
  await getAllExternalUsers()
})

const getAllExternalUsers = async () => {
  try {
    const { data } = await axios.get('/api/external_users')
    externalUsers.value = data.users
  } catch (error) {
    console.log(error)
  }
}

const getExternalUser = async id => {
  try {
    const { data } = await axios.get('/api/external_user/' + id)
    activeExternalUser.value = data.user
  } catch (error) {
    console.log(error)
  }
}

const saveExternalUser = async user => {
  if (!user.id) {
    try {
      const { data } = await axios.post('/api/external_user/', { user })
    } catch (e) {
      store.addMessage(e.response.data.error, 'danger')
      return
    }
  } else {
    try {
      const { data } = await axios.put('/api/external_user/' + user.id, { user })
    } catch (e) {
      store.addMessage(e.response.data.error, 'danger')
      return
    }
  }
  await getAllExternalUsers()
  activeExternalUser.value = null
  store.addMessage('Ekstern bruker lagret.', 'success')
}

const deleteExternalUser = async user => {
  try {
    const { data } = await axios.delete('/api/external_user/' + user.id)
  } catch (error) {
    console.log(error)
  }
  await getAllExternalUsers()
  activeExternalUser.value = null
  store.addMessage('Ekstern bruker slettet.', 'success')
}

const addExternalUser = () => {
  activeExternalUser.value = {
    name: '',
    userId: '',
  }
}

const membershipsString = computed({
  get() {
    if (!activeExternalUser.value || !activeExternalUser.value.memberships) {
      return ''
    }
    return JSON.stringify(activeExternalUser.value.memberships, null, 2)
  },
  set(value) {
    if (value) {
      try {
        activeExternalUser.value.memberships = JSON.parse(value)
      } catch (e) {
        console.error('Invalid JSON format for memberships:', e)
      }
    } else {
      activeExternalUser.value.memberships = []
    }
  },
})
</script>

<template>
  <!-- modal -->
  <div
    class="modal fade"
    id="editAuthor"
    tabindex="-1"
    aria-labelledby="editUserLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div v-if="activeExternalUser" class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="editUserLabel">{{ activeExternalUser.name }}</h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>

        <div class="modal-body">
          <div class="mb-3">
            <label for="name" class="form-label mt-2">Navn</label>
            <input
              type="text"
              class="form-control"
              id="name"
              v-model="activeExternalUser.name"
              maxlength="50"
            />
            <div class="form-text text-end">{{ activeExternalUser.name.length }}/50</div>
          </div>
          <div class="mb-3">
            <label for="username" class="form-label">Brukernavn</label>
            <input
              type="text"
              class="form-control"
              id="username"
              v-model="activeExternalUser.username"
            />
          </div>
          <div class="mb-3">
            <label for="username" class="form-label mt-2">Passord</label>
            <div class="input-group">
              <input
                :type="showPassword ? 'text' : 'password'"
                class="form-control"
                id="password"
                v-model="activeExternalUser.newPassword"
              />
              <button
                type="button"
                class="btn btn-outline-secondary mb-0"
                @click="showPassword = !showPassword"
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
          <div class="mb-3">
            <label for="hasSelfService" class="form-label mt-2">Har 'Min side'</label>
            <input
              class="form-check-input m-2"
              type="checkbox"
              v-model="activeExternalUser.hasSelfService"
              id="hasSelfService"
            />
          </div>
          <div class="mb-3">
            <label for="validTo" class="form-label mt-2">Gyldig til</label>
            <VueDatePicker
              id="validTo"
              v-model="activeExternalUser.validTo"
              locale="nb"
              select-text="Velg"
              cancel-text="Avbryt"
              :clearable="false"
              :min-date="new Date()"
              preview-format="dd.MM HH:mm"
            ></VueDatePicker>
          </div>
          <div class="mb-3">
            <label for="memberships" class="form-label mt-2">Medlemsskap (Json)</label>
            <textarea
              class="form-control"
              id="memberships"
              rows="3"
              v-model="membershipsString"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-primary"
            data-bs-dismiss="modal"
            @click="saveExternalUser(activeExternalUser)"
          >
            Lagre
          </button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Lukk</button>
        </div>
      </div>
    </div>
  </div>

  <!-- modal -->
  <div
    class="modal fade"
    id="deleteUserConfirm"
    tabindex="-1"
    aria-labelledby="deleteAuthorConfirmLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="deleteAuthorConfirmLabel">Ekstern bruker</h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div v-if="activeExternalUser" class="modal-body">
          Vil du virkelig slette {{ activeExternalUser.name }}?
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-warning"
            data-bs-dismiss="modal"
            @click="deleteExternalUser(activeExternalUser)"
          >
            Slett
          </button>
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Lukk</button>
        </div>
      </div>
    </div>
  </div>

  <div class="card mt-3">
    <div class="card-body">
      <h2 class="h4">Eksterne brukere</h2>
      <ul class="list-group mb-2">
        <li v-for="user in externalUsers" class="list-group-item">
          <div class="row">
            <div class="col-4">{{ user.name }}</div>
            <div class="col-2">{{ user.username }}</div>
            <div class="col-1">
              <span v-if="user.expired" class="badge bg-danger">Utløpt</span>
            </div>
            <div class="col">
              <button
                type="button"
                class="btn btn-secondary"
                data-bs-toggle="modal"
                data-bs-target="#editAuthor"
                @click="getExternalUser(user.id)"
              >
                Endre / Detaljer
              </button>
              <button
                type="button"
                class="btn btn-warning"
                data-bs-toggle="modal"
                data-bs-target="#deleteUserConfirm"
                @click="getExternalUser(user.id)"
              >
                Slett
              </button>
            </div>
          </div>
        </li>
      </ul>
      <button
        class="btn btn-secondary ms-0"
        data-bs-toggle="modal"
        data-bs-target="#editAuthor"
        @click="addExternalUser"
      >
        Legg til ekstern bruker
      </button>
    </div>
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
