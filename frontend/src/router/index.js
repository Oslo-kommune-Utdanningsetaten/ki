import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import BotView from '../views/BotView.vue'
import ImgBotView from '../views/ImgBotView.vue'
import EditBotView from '../views/EditBotView.vue'
import InfoView from '../views/InfoView.vue'
import SettingsView from '../views/SettingsView.vue'
import MessageView from '../views/MessageView.vue'
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
    path: '/info/:page',
    name: 'info',
    component: InfoView,
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const loginUrl = '/auth/feidelogin'

  if (to.meta?.requiresAuth) {
    if (store.isAuthenticated === true) {
      // Proceed if user is authenticated
      next()
    } else if (store.isAuthenticated === false) {
      // Redirect to login page
      window.location.href = loginUrl
    } else {
      // Authentication status unknown, check with the server
      try {
        const response = await axios.get('/api/menu_items')
        const isAuthenticatedHeader = response.headers['x-is-authenticated']
        if (isAuthenticatedHeader === 'true') {
          store.isAuthenticated = true
          next()
        } else {
          store.isAuthenticated = false
          window.location.href = loginUrl
        }
      } catch (error) {
        // The interceptor handles 401 and 403 errors
        console.error('Error checking authentication:', error)
      }
    }
  } else {
    next()
  }
})

export default router
