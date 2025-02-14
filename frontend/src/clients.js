import axios from 'axios'
import { store } from './store'

export const axiosInstance = axios.create({
  withCredentials: true,
})

const errorInterceptor = error => {
  if (axios.isAxiosError(error)) {
    const axiosError = error

    if (axiosError.response?.status === 401) {
      // Unauthorized user
      store.resetStore()
      window.location.href = '/auth/feidelogin'
    } else if (axiosError.response?.status === 403) {
      store.addMessage('Du har visst ikke tilgang her', 'danger', { isMessagePersistent: true })
    }
  }

  return Promise.reject(error)
}

axiosInstance.interceptors.response.use(response => response, errorInterceptor)
