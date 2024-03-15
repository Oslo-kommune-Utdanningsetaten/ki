import { reactive } from 'vue'

export const store = reactive({
  messages: [],
  removeMessage(index) {
    this.messages.splice(index, 1)
  },
  addMessage(text, type) {
    this.messages.push({ 'text': text, 'type': type })
  }
})