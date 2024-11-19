import { reactive } from 'vue'

export const store = reactive({
  isAdmin: false,
  isEmployee: false,
  editGroups: false,
  messages: [],
  isAuthenticated: null,

  logout() {
    fetch('/auth/logout/', {
      method: 'GET',
      credentials: 'include',
    })
      .then(() => {
        this.isAuthenticated = false
        window.location.href = '/'
      })
      .catch(error => {
        console.error('Error logging out:', error)
      })
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
