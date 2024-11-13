import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import BotView from '../views/BotView.vue'
import ImgBotView from '../views/ImgBotView.vue'
import EditBotView from '../views/EditBotView.vue'
import InfoView from '../views/InfoView.vue'
import SettingsView from '../views/SettingsView.vue'
import MessageView from '../views/MessageView.vue'

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

  if (to.meta && to.meta.requiresAuth) {
    try {
      const response = await fetch('/auth/is_authenticated/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      if (response.ok) {
        const data = await response.json()
        if (data.isAuthenticated) {
          next()
        } else {
          window.location.href = loginUrl
        }
      } else {
        window.location.href = loginUrl
      }
    } catch (error) {
      console.error('Error checking authentication:', error)
      next({ name: 'home' })
    }
  } else {
    next()
  }
})

export default router
