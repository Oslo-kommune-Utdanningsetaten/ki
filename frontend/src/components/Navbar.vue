<script setup>
import { RouterLink } from 'vue-router'
import { axiosInstance as axios } from '../clients'
import { onMounted, computed, ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { store } from '../store.js'

const infoPages = ref([])

const getAppConfig = async () => {
  try {
    const { data } = await axios.get('/api/app_config')
    infoPages.value = data.info_pages
    store.isAdmin = data.role ? data.role.is_admin : false
    store.isEmployee = data.role ? data.role.is_employee : false
    store.isAuthor = data.role ? data.role.is_author : false
    store.defaultModel = data.default_model
  } catch (error) {
    if (error.response && error.response.status === 401) {
      window.location.href = '/auth/feidelogin'
    } else {
      console.log(error)
    }
  }
}

watchEffect(() => {
  const route = useRoute()
  getAppConfig()
})
</script>

<template>
  <header>
    <div id="header" class="d-flex justify-content-between p-4 oslo-bg-light">
      <RouterLink active-class="active" class="nav-link" to="/">
        <h1 class="h3 p-3">Kunstig intelligens for Osloskolen</h1>
      </RouterLink>
      <RouterLink active-class="active" class="logo" to="/">
        <img src="@/assets/img/oslo_logo_sort.svg" alt="Oslologo" />
      </RouterLink>
    </div>
  </header>

  <nav class="d-flex flex-row-reverse">
    <!-- TODO use store for this -->
    <div v-if="infoPages.length === 0" class="nav-item">
      <a class="nav-link p-3" href="/auth/feidelogin">Logg inn</a>
    </div>
    <div v-else class="nav-item">
      <a class="nav-link p-3" href="/auth/logout">Logg ut</a>
    </div>
    <a v-if="store.isAdmin" data-bs-toggle="dropdown" class="nav-link p-3 dropdown-toggle" href="#">
      Administrasjon
    </a>
    <ul v-if="store.isAdmin" class="dropdown-menu">
      <RouterLink class="dropdown-item" to="/school_accesses">Skoletilgang</RouterLink>
      <RouterLink class="dropdown-item" to="/authors">Forfattere</RouterLink>
      <RouterLink class="dropdown-item" to="/settings">Innstillinger</RouterLink>
    </ul>
    <div v-for="item in infoPages" :key="item.id" class="nav-item">
      <RouterLink activeClass="active" class="nav-link p-3" :to="item.url">
        {{ item.title }}
      </RouterLink>
    </div>
    <div class="nav-item">
      <RouterLink activeClass="active" class="nav-link p-3" to="/">Startside</RouterLink>
    </div>
  </nav>
</template>

<style scoped>
.active {
  font-weight: bold;
}
</style>
