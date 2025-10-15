<script setup>
import { RouterLink } from 'vue-router'
import { axiosInstance as axios } from '../clients'
import { onMounted, computed, ref, watchEffect } from 'vue'
import { useRoute } from 'vue-router'
import { store } from '../store.js'

const infoPages = ref([])
const isActiveAdminHeader = ref(false)
const isActiveInfoHeader = ref(false)
const route = useRoute()

let firstRouteHandled = false

const getAppConfig = async () => {
  try {
    const response = await axios.get('/api/app_config')
    const data = response.data
    infoPages.value = data.infoPages
    store.isAuthenticated = response.headers['x-is-authenticated'] === 'true'
    store.isAdmin = data.role ? data.role.isAdmin : false
    store.isEmployee = data.role ? data.role.isEmployee : false
    store.isAuthor = data.role ? data.role.isAuthor : false
    // store.isExternalUser = data.role ? data.role.isExternalUser : false
    store.hasSelfService = data.role ? data.role.hasSelfService : false
    store.defaultModel = data.defaultModel
    store.maxMessageLength = data.maxMessageLength
  } catch (error) {
    if (error.response && error.response.status === 401) {
      window.location.href = '/auth/feidelogin'
    } else {
      console.log(error)
    }
  }
}

watchEffect(() => {
  // Initial fetch
  if (!firstRouteHandled) {
    getAppConfig()
    firstRouteHandled = true
  }
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
            <ul class="navbar-nav mb-2 mb-lg-0">
              <li class="nav-item">
                <RouterLink activeClass="active" class="nav-link ps-0" aria-current="page" to="/">
                  Startside
                </RouterLink>
              </li>
              <li v-if="infoPages.length > 1" class="nav-item dropdown" id="infoHeader">
                <a
                  class="nav-link dropdown-toggle"
                  href="#"
                  role="button"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  Informasjon
                </a>
                <ul class="dropdown-menu">
                  <li v-for="item in infoPages" :key="item.id">
                    <RouterLink class="dropdown-item" active-class="active" :to="item.url">
                      {{ item.title }}
                    </RouterLink>
                  </li>
                </ul>
              </li>
              <li v-else-if="infoPages.length == 1" class="nav-item">
                <RouterLink activeClass="active" class="nav-link" :to="infoPages[0].url">
                  {{ infoPages[0].title }}
                </RouterLink>
              </li>

              <li v-if="store.isAdmin" class="nav-item dropdown" id="adminHeader">
                <a
                  class="nav-link dropdown-toggle"
                  href="#"
                  role="button"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                >
                  Administrasjon
                </a>
                <ul class="dropdown-menu">
                  <li>
                    <RouterLink class="dropdown-item" active-class="active" to="/school_accesses">
                      Skoletilgang
                    </RouterLink>
                  </li>
                  <li>
                    <RouterLink class="dropdown-item" active-class="active" to="/authors">
                      Forfattere
                    </RouterLink>
                  </li>
                  <li>
                    <RouterLink class="dropdown-item" active-class="active" to="/externalusers">
                      Eksterne brukere
                    </RouterLink>
                  </li>
                  <li>
                    <RouterLink class="dropdown-item" active-class="active" to="/settings">
                      Innstillinger
                    </RouterLink>
                  </li>
                </ul>
              </li>
              <li v-if="store.hasSelfService" class="nav-item">
                <RouterLink activeClass="active" class="nav-link" to="/externaluser">
                  Min side
                </RouterLink>
              </li>
              <li v-if="store.isAuthenticated === true" class="nav-item ms-auto">
                <a class="nav-link" href="/auth/logout">Logg ut</a>
              </li>
              <li v-else class="nav-item ms-auto">
                <a class="nav-link" href="/auth/feidelogin">Logg inn</a>
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
