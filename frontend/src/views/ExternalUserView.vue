<script setup>
import { useRoute } from 'vue-router'
import { useRouter } from 'vue-router'
import { store } from '../store'
import { axiosInstance as axios } from '../clients'
import { ref, watchEffect } from 'vue'

const user = ref({
  id: null,
  username: '',
  name: '',
  password: '',
  newPassword: '',
})
const showPassword = ref(false)

watchEffect(() => {
  getUserInfo()
})

async function getUserInfo() {
  try {
    const { data } = await axios.get('/api/external_user_info')
    user.value = data.user
  } catch (error) {
    console.log(error)
  }
}

async function saveUserInfo() {
  try {
    await axios.put('/api/external_user_info/', { user: user.value })
    store.addMessage('Endringen er lagret', 'success')
  } catch (e) {
    store.addMessage(e.response.data.error, 'danger')
  }
  user.value.password = ''
}
</script>

<template>
  <form class="container mt-3">
    <div class="mb-3 row">
      <label for="username" class="col-sm-2 col-form-label">Brukernavn</label>
      <div class="col-sm-10">
        <div class="form-control-plaintext">
          {{ user.username }}
        </div>
      </div>
      <label for="name" class="col-sm-2 col-form-label">Navn</label>
      <div class="col-sm-10">
        <input
          type="text"
          class="form-control"
          id="name"
          placeholder="Skriv inn navn"
          v-model="user.name"
        />
      </div>
      <label for="inputPassword" class="col-sm-2 col-form-label">Gammelt passord</label>
      <div class="col-sm-10">
        <div class="input-group">
          <input
            :type="showPassword ? 'text' : 'password'"
            class="form-control"
            id="inputPassword"
            placeholder="Skriv inn gammelt passord"
            v-model="user.password"
          />
          <button
            type="button"
            class="btn btn-outline-secondary"
            @click="(showPassword = !showPassword)"
          >
            {{ showPassword ? 'Skjul' : 'Vis' }}
          </button>
        </div>
      </div>
      <label for="inputNewPassword" class="col-sm-2 col-form-label">Nytt passord</label>
      <div class="col-sm-10">
        <div class="input-group">
          <input
            :type="showPassword ? 'text' : 'password'"
            class="form-control"
            id="inputNewPassword"
            placeholder="Skriv inn nytt passord"
            v-model="user.newPassword"
          />
          <button
            type="button"
            class="btn btn-outline-secondary"
            @click="(showPassword = !showPassword)"
          >
            {{ showPassword ? 'Skjul' : 'Vis' }}
          </button>
        </div>
      </div>
    </div>

    <button type="submit" @click.prevent="saveUserInfo" class="btn btn-primary">Lagre</button>
  </form>
</template>
