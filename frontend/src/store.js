import { reactive } from 'vue'
import { axiosInstance as axios } from './clients'

export const store = reactive({
  isAdmin: false,
  isEmployee: false,
  isAuthor: false,
  editGroups: false,
  messages: [],
  isAuthenticated: null,
  defaultModel: {},

  logout() {
    axios
      .get('/auth/logout/')
      .then(() => {
        this.resetStore()
        window.location.href = '/'
      })
      .catch(error => {
        console.error('Error logging out:', error)
      })
  },

  resetStore() {
    this.isAdmin = false
    this.isEmployee = false
    this.isAuthor = false
    this.editGroups = false
    this.messages = []
    this.isAuthenticated = false
  },

  removeMessage(index) {
    this.messages.splice(index, 1)
  },
  removeMessageId(id) {
    this.messages.splice(
      this.messages.findIndex(x => x.id === id),
      1
    )
  },
  addMessage(text, type) {
    const uuid = crypto.randomUUID()
    this.messages.push({ id: uuid, text: text, type: type })
    setTimeout(() => {
      this.removeMessageId(uuid)
    }, 5000)
  },
})
