import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import BotView from '../views/BotView.vue'
import ImgBotView from '../views/ImgBotView.vue'
import EditBotView from '../views/EditBotView.vue'
import InfoView from '../views/InfoView.vue'
import SettingsView from '../views/SettingsView.vue'
import MessageView from '../views/MessageView.vue'
import { store } from '../store'

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

router.beforeEach(async (to, from) => {
  const loginUrl = '/auth/feidelogin';

  if (to.meta && to.meta.requiresAuth) {
    if (store.isAuthenticated === true) {
      // Proceed if user is authenticated
      return true;
    } else if (store.isAuthenticated === false) {
      // If user is not authenticated redirect to login page
      window.location.href = loginUrl;
      return false; // Abort navigation
    } else {
      // Authentication status unknown check with the server
      try {
        const response = await fetch('/api/menu_items', {
          method: 'GET',
          credentials: 'include',
        });
        const isAuthenticatedHeader = response.headers.get('X-Is-Authenticated');
        if (isAuthenticatedHeader === 'true') {
          store.isAuthenticated = true;
          return true;
        } else {
          store.isAuthenticated = false;
          window.location.href = loginUrl;
          return false; 
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
        store.isAuthenticated = false;
        window.location.href = loginUrl;
        return false; 
      }
    }
  } else {
    return true;
  }
});

export default router
