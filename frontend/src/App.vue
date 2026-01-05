<script setup>
import { RouterView } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import Messages from '@/components/Messages.vue'
import { onMounted } from 'vue'
import { axiosInstance as axios } from '@/clients'
import { store } from '@/store.js'

const getAppConfig = async () => {
  try {
    const response = await axios.get('/api/app_config')
    const data = response.data
    store.isAuthenticated = response.headers['x-is-authenticated'] === 'true'
    store.isAdmin = data.role ? data.role.isAdmin : false
    store.isAdminAvailable = data.role ? data.role.isAdminAvailable : false
    store.isEmployee = data.role ? data.role.isEmployee : false
    store.isAuthor = data.role ? data.role.isAuthor : false
    store.hasSelfService = data.role ? data.role.hasSelfService : false
    store.defaultModel = data.defaultModel
    store.maxMessageLength = data.maxMessageLength
    store.isAudioModifiableByEmployees = data.isAudioModifiableByEmployees
  } catch (error) {
    if (error.response && error.response.status === 401) {
      window.location.href = '/auth/feidelogin'
    } else {
      console.log(error)
    }
  }
}

onMounted(() => {
  getAppConfig()
})
</script>

<template>
  <Navbar />
  <div class="container mt-3">
    <Messages />
    <RouterView />
  </div>
</template>

<style scoped>
@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-Light.woff');
  font-weight: normal;
  font-style: normal;
}

@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-LightItalic.woff');
  font-weight: normal;
  font-style: italic;
}

@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-Regular.woff');
  font-weight: 500;
  font-style: normal;
}

@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-RegularItalic.woff');
  font-weight: 500;
  font-style: italic;
}

@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-Medium.woff');
  font-weight: bold;
  font-style: normal;
}

@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-MediumItalic.woff');
  font-weight: bold;
  font-style: italic;
}
/* 
@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-Bold.woff');
  font-weight: 700;
  font-style: normal;
}

@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-BoldItalic.woff');
  font-weight: 700;
  font-style: italic;
}
 */
</style>
