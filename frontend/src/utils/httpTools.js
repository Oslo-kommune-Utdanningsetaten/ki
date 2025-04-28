import { axiosInstance as axios } from '../clients'
import { store } from '../store.js'


export const getCookie = name => {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

export const getUser = async () => {
  try {
    const { data } = await axios.get('/api/user_info/')
    return data.user
  } catch (error) {
    console.log(error)
  }
}

export const getBot = async (botId) => {
  try {
    const { data } = await axios.get('/api/bot_info/' + botId)
    return data.bot
  } catch (error) {
    console.log(error)
  }
}

export const deleteBot = async (botId) => {
  try {
    await axios.delete('/api/bot_info/' + botId)
    store.addMessage('Boten er nå slettet', 'info')
  } catch (error) {
    console.log(error)
  }
}

export const submitTextPrompt = async (data, onProgressCallback) => {
  const csrfToken = getCookie('csrftoken')
  return await axios
    .post('/api/send_message', data, {
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      responseType: 'stream',
      onDownloadProgress: progressEvent => {
        // axios doesn't support streaming on post, so we need to update messages manually on download progress
        onProgressCallback(progressEvent.event.target.responseText)
      },
    })
    .catch(error => {
      console.error('Something went wrong while streaming the chat response', error)
    })
}

export const submitImagePrompt = async (data) => {
  try {
    const result = await axios.post(
      '/api/send_img_message',
      data,
      {
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        }
      }
    )
    return { revisedPrompt: result.data.revised_prompt, imageUrl: result.data.url, systemMessage: result.data.system_message }
  } catch (error) {
    console.log(error)
  }
}



