<script setup>
import { ref } from 'vue'
import { store } from '../store.js'
import { submitLogin } from '../utils/httpTools.js'

const loginUserName = ref('')
const loginUserPassword = ref('')
const showPassword = ref(false)

const sendLogin = async () => {
  store.isExternalUser = true
  try {
    const { data } = await submitLogin({
      username: loginUserName.value,
      password: loginUserPassword.value,
    })
    if (data.error) {
      loginUserPassword.value = ''
      store.resetStore()
      store.addMessage(data.error, 'danger')
    } else {
      loginUserName.value = ''
      loginUserPassword.value = ''
      window.location.href = '/'
    }
  } catch (e) {
    console.log('Error during login:', e)
  }
}
</script>
<template>
  <div class="row justify-content-center mt-5">
    <div class="card mb-3" style="width: 30rem">
      <form @submit.prevent="sendLogin">
        <div class="card-body">
          <h1 class="h3 card-title">Logg inn med demobruker</h1>
          <input
            type="text"
            class="form-control"
            id="username"
            v-model="loginUserName"
            required
            placeholder="Brukernavn"
          />
          <div class="input-group mt-2">
            <input
              :type="showPassword ? 'text' : 'password'"
              class="form-control"
              id="password"
              v-model="loginUserPassword"
              placeholder="Passord"
            />
            <button
              type="button"
              class="btn btn-outline-secondary mb-0"
              @click="showPassword = !showPassword"
            >
              <img v-if="showPassword" src="@/components/icons/eye-hide.svg" alt="Skjul passord" />
              <img v-else src="@/components/icons/eye-show.svg" alt="Vis passord" />
            </button>
          </div>
        </div>
        <div class="d-flex justify-content-end">
          <button type="submit" class="btn btn-primary">Logg inn</button>
        </div>
      </form>
    </div>
  </div>
</template>
