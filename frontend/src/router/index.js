import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import BotView from '../views/BotView.vue'
import ImgBotView from '../views/ImgBotView.vue'
import EditBotView from '../views/EditBotView.vue'
import DistributeBotView from '../views/DistributeBotView.vue'
import InfoView from '../views/InfoView.vue'
import SettingsView from '../views/SettingsView.vue'
import SchoolAccessesView from '../views/SchoolAccessesView.vue'
import AuthorsView from '../views/AuthorsView.vue'
import AdminExternalUsersView from '../views/AdminExternalUsersView.vue'
import MessageView from '../views/MessageView.vue'
import ExternalUserView from '../views/ExternalUserView.vue'
import ExternalUserLogin from '../views/ExternalUserLogin.vue'
import { store } from '../store'
import { axiosInstance as axios } from '../clients'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/message/:text/:type',
    name: 'message',
    component: MessageView,
  },
  {
    path: '/bot/:id',
    name: 'bot',
    component: BotView,
    meta: { requiresAuth: true },
  },
  {
    path: '/imgbot/:id',
    name: 'imgbot',
    component: ImgBotView,
    meta: { requiresAuth: true },
  },
  {
    path: '/editbot/:method/:id?',
    name: 'editbot',
    component: EditBotView,
    meta: { requiresAuth: true },
  },
  {
    path: '/distribute/:id',
    name: 'distribute',
    component: DistributeBotView,
    meta: { requiresAuth: true },
  },
  {
    path: '/info',
    name: 'info_new',
    component: InfoView,
    meta: { requiresAuth: false },
  },
  {
    path: '/info/:slug',
    name: 'info',
    component: InfoView,
    meta: { requiresAuth: false },
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView,
    meta: { requiresAuth: true },
  },
  {
    path: '/school_accesses',
    name: 'school_accesses',
    component: SchoolAccessesView,
    meta: { requiresAuth: true },
  },
  {
    path: '/authors',
    name: 'authors',
    component: AuthorsView,
    meta: { requiresAuth: true },
  },
  {
    path: '/externalusers',
    name: 'externalUsers',
    component: AdminExternalUsersView,
    meta: { requiresAuth: true },
  },
  {
    path: '/externaluser/',
    name: 'externalUser',
    component: ExternalUserView,
    meta: { requiresAuth: true },
  },
  {
    path: '/demo/',
    name: 'ExternalUserLogin',
    component: ExternalUserLogin,
    meta: { requiresAuth: false },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to, from) => {
  const loginUrl = '/auth/feidelogin'

  if (to.meta?.requiresAuth) {
    if (store.isAuthenticated === true) {
      // Proceed if user is authenticated
      return true
    } else if (store.isAuthenticated === false) {
      // Redirect to login page
      // window.location.href = loginUrl
      return false
    } else {
      // Authentication status unknown, check with the server
      try {
        const response = await axios.get('/api/app_config')
        const isAuthenticatedHeader = response.headers['x-is-authenticated']
        if (isAuthenticatedHeader === 'true') {
          store.isAuthenticated = true
          return true
        } else {
          store.isAuthenticated = false
          window.location.href = loginUrl
          next(false)
        }
      } catch (error) {
        // The interceptor handles 401 and 403 errors
        console.error('Error checking authentication:', error)
        return false
      }
    }
  } else {
    return true
  }
})

export default router
