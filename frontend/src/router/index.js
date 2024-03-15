import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import BotView from '../views/BotView.vue'
import EditBotView from '../views/EditBotView.vue'
import InfoView from '../views/InfoView.vue'
import SettingsView from '../views/SettingsView.vue'
import MessageView from '../views/MessageView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/message/:text/:type',
      name: 'message',
      component: MessageView
    },
    {
      path: '/bot/:id',
      name: 'bot',
      component: BotView
    },
    {
      path: '/editbot',
      name: 'newbot',
      component: EditBotView
    },
    {
      path: '/editbot/:id',
      name: 'editbot',
      component: EditBotView
    },
    {
      path: '/info/:page',
      name: 'info',
      component: InfoView
    },
    {
      path: '/settings',
      name: 'settings',
      component: SettingsView
    }
  ]
})

export default router
