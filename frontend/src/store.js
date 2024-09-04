import { reactive } from 'vue'

export const store = reactive({
  isAdmin: false,
  isEmployee: false,
  editGroups: false,
  messages: [],
  removeMessage(index) {
    this.messages.splice(index, 1)
  },
  removeMessageId(id) {
    this.messages.splice(
      this.messages.findIndex((x) => x.id === id),
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
