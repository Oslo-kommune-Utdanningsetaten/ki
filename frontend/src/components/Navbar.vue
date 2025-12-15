<script setup>
import { RouterLink } from 'vue-router'
import { axiosInstance as axios } from '../clients'
import { onMounted, computed, ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { store } from '../store.js'

const infoPages = ref([])
const route = useRoute()

const getAppConfig = async () => {
  try {
    const response = await axios.get('/api/app_config')
    const data = response.data
    infoPages.value = data.infoPages
    store.isAuthenticated = response.headers['x-is-authenticated'] === 'true'
    store.isAdmin = data.role ? data.role.isAdmin : false
    store.isAdminAvailable = data.role ? data.role.isAdminAvailable : false
    store.isEmployee = data.role ? data.role.isEmployee : false
    store.isAuthor = data.role ? data.role.isAuthor : false
    // store.isExternalUser = data.role ? data.role.isExternalUser : false
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

const closeDropdown = event => {
  const dropdown = event.target.closest('.dropdown')
  if (dropdown) {
    dropdown.classList.remove('show')
    dropdown.querySelector('.dropdown-menu')?.classList.remove('show')
  }
}

const toggleAdmin = async event => {
  event.preventDefault()
  // closeDropdown(event)
  try {
    store.isAdmin = (await axios.put('/api/admin_toggle')).data.isAdmin
  } catch (error) {
    console.log(error)
  }
}

onMounted(() => {
  getAppConfig()
})
</script>

<template>
  <header>
    <div id="header" class="pt-4 oslo-bg-light">
      <div class="container d-flex justify-content-between align-items-center">
        <RouterLink class="nav-link" to="/">
          <h1 class="h3">Kunstig intelligens for Osloskolen</h1>
        </RouterLink>
        <RouterLink class="logo" to="/">
          <img src="@/assets/img/oslo_logo_sort.svg" alt="Oslologo" />
        </RouterLink>
      </div>

      <nav class="navbar navbar-expand-lg">
        <div class="container">
          <button
            class="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbar"
            aria-controls="navbar"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbar">
            <ul class="navbar-nav me-auto mb-2 mb-lg-0">
              <li v-if="store.isAuthenticated" class="nav-item">
                <RouterLink
                  active-class="active"
                  class="nav-link ps-0"
                  aria-current="page"
                  to="/"
                  @click="closeDropdown"
                >
                  Boter
                </RouterLink>
              </li>
              <li v-if="infoPages.length > 1" class="nav-item dropdown" id="infoHeader">
                <a
                  class="nav-link dropdown-toggle"
                  :class="{ active: route.name === 'info' }"
                  href="#"
                  role="button"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  Informasjon
                </a>
                <ul class="dropdown-menu">
                  <li v-for="item in infoPages" :key="item.id">
                    <RouterLink
                      class="dropdown-item"
                      active-class="active"
                      :to="item.url"
                      @click="closeDropdown"
                    >
                      {{ item.title }}
                    </RouterLink>
                  </li>
                </ul>
              </li>
              <li v-else-if="infoPages.length == 1" class="nav-item">
                <RouterLink active-class="active" class="nav-link" :to="infoPages[0].url">
                  {{ infoPages[0].title }}
                </RouterLink>
              </li>
            </ul>
            <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
              <li v-if="!store.isAdmin && store.isAdminAvailable" class="nav-item">
                <a class="nav-link" active-class="active" href="" @click="toggleAdmin">
                  Aktiver administrator
                </a>
              </li>

              <li v-if="store.isAdmin" class="nav-item dropdown" id="adminHeader">
                <a
                  class="nav-link dropdown-toggle"
                  :class="{ active: route.path.startsWith('/admin') }"
                  href="#"
                  role="button"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  Administrator
                </a>
                <ul class="dropdown-menu">
                  <li>
                    <RouterLink
                      class="dropdown-item"
                      active-class="active"
                      :to="{ name: 'schoolAccesses' }"
                      @click="closeDropdown"
                    >
                      Skoletilgang
                    </RouterLink>
                  </li>
                  <li>
                    <RouterLink
                      class="dropdown-item"
                      active-class="active"
                      :to="{ name: 'authors' }"
                      @click="closeDropdown"
                    >
                      Forfattere
                    </RouterLink>
                  </li>
                  <li>
                    <RouterLink
                      class="dropdown-item"
                      active-class="active"
                      :to="{ name: 'externalUsers' }"
                      @click="closeDropdown"
                    >
                      Eksterne brukere
                    </RouterLink>
                  </li>
                  <li>
                    <RouterLink
                      class="dropdown-item"
                      active-class="active"
                      :to="{ name: 'settings' }"
                      @click="closeDropdown"
                    >
                      Innstillinger
                    </RouterLink>
                  </li>
                  <li>
                    <a class="dropdown-item" active-class="active" href="" @click="toggleAdmin">
                      Deaktiver administrator
                    </a>
                  </li>
                </ul>
              </li>
              <li v-if="store.hasSelfService" class="nav-item">
                <RouterLink active-class="active" class="nav-link" to="/externaluser">
                  Min side
                </RouterLink>
              </li>
              <li class="nav-item">
                <a v-if="store.isAuthenticated" class="nav-link pe-0" href="/auth/logout">
                  Logg ut
                </a>
                <a v-else class="nav-link pe-0" href="/auth/feidelogin">Logg inn</a>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.active {
  font-weight: bold;
}
</style>
