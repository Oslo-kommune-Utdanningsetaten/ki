import { marked } from 'marked'
import DOMPurify from 'dompurify'


// Each entry in the colors array is a pair of colors used in the bot avatar
const colors = [
  ['oslo-fill-blue', 'oslo-fill-dark-blue'],
  ['oslo-fill-yellow', 'oslo-fill-black'],
  ['oslo-fill-green', 'oslo-fill-dark-green'],
  ['oslo-fill-red', 'oslo-fill-black'],
  ['oslo-fill-dark-beige', 'oslo-fill-black'],
]

// Takes an array of values, where each describes a body part of the bot avatar
// Returns an object where the various parts are described in detail
export const createBotDescriptionFromScheme = (scheme) => {
  const defaultScheme = [0, 0, 0, 0, 0, 0, 0]
  const [colorValue, headValue, eyesValue, hairValue, earsValue, armsValue, neckValue] = scheme && scheme.length === 7 ? scheme : defaultScheme

  // Empty bot object
  const bot = {
    hair: { shapes: [] },
    head: { shapes: [] },
    eyes: { shapes: [] },
    ears: { shapes: [] },
    neck: { shapes: [] },
    body: { shapes: [] },
    arms: { shapes: [] },
  }

  // Translate the values to human readable descriptions for easier reference
  bot.head.description = headValue === 0 ? 'low' : headValue === 1 ? 'high' : 'slanted'
  bot.eyes.description = eyesValue === 0 ? 'round' : eyesValue === 1 ? 'square' : eyesValue === 2 ? 'rect' : 'wink'
  bot.hair.description = hairValue === 0 ? 'absent' : hairValue === 1 ? 'flat' : 'scruffy'
  bot.ears.description = earsValue === 1 ? 'present' : 'absent'
  bot.arms.description = armsValue === 1 ? 'shoulder' : 'straight'
  bot.neck.description = neckValue === 1 ? 'thin' : 'thick'

  // Hair
  if (bot.hair.description === 'flat') {
    bot.hair.shapes.push({
      x: 2,
      y: 0,
      width: 8,
      height: 2,
      type: 'rect',
      color: colors[colorValue][1]
    })
  } else if (bot.hair.description === 'scruffy') {
    bot.hair.shapes.push({
      type: 'polygon',
      points: '2,0 10,0 10,2 9,2 9,1 8,1 8,2 6,2 6,1 5,1 5,2 4,2 4,1 3,1 3,2 2,2 2,0',
      color: colors[colorValue][1]
    })
  }

  // Head
  if (bot.head.description === 'slanted') {
    bot.head.shapes.push({
      type: 'polygon',
      points: '2,0 10,0 10,6 6,8 2,6',
      color: colors[colorValue][0]
    })
  } else {
    bot.head.shapes.push({
      x: 2,
      y: 0,
      width: 8,
      height: bot.head.description === 'high' ? 4 : 8,
      type: 'rect',
      color: colors[colorValue][0]
    })
  }

  // Eyes
  const eyePositionY = bot.head.description === 'high' ? 1 : 3
  if (bot.eyes.description === 'square') {
    bot.eyes.shapes.push({
      x: 3,
      y: eyePositionY,
      width: 2,
      height: 2,
      type: 'rect',
      color: colors[colorValue][1]
    })
    bot.eyes.shapes.push({
      x: 7,
      y: eyePositionY,
      width: 2,
      height: 2,
      type: 'rect',
      color: colors[colorValue][1]
    })
  } else if (bot.eyes.description === 'wink') {
    bot.eyes.shapes.push({
      x: 3,
      y: eyePositionY,
      width: 2,
      height: 2,
      type: 'rect',
      color: colors[colorValue][1]
    })
    bot.eyes.shapes.push({
      x: 7,
      y: eyePositionY,
      width: 2,
      height: 1,
      type: 'rect',
      color: colors[colorValue][1]
    })
  } else if (bot.eyes.description === 'rect') {
    bot.eyes.shapes.push({
      x: 3,
      y: eyePositionY,
      width: 2,
      height: 1,
      type: 'rect',
      color: colors[colorValue][1]
    })
    bot.eyes.shapes.push({
      x: 7,
      y: eyePositionY,
      width: 2,
      height: 1,
      type: 'rect',
      color: colors[colorValue][1]
    })
  } else {
    bot.eyes.shapes.push({
      type: 'circle',
      cx: 4,
      cy: eyePositionY + 1,
      r: 1,
      color: colors[colorValue][1]
    })
    bot.eyes.shapes.push({
      type: 'circle',
      cx: 8,
      cy: eyePositionY + 1,
      r: 1,
      color: colors[colorValue][1]
    })
  }

  // Ears, same Y position as eyes
  if (bot.ears.description === 'present') {
    bot.ears.shapes.push({
      x: 1,
      y: eyePositionY,
      width: 1,
      height: 2,
      type: 'rect',
      color: colors[colorValue][1]
    })
    bot.ears.shapes.push({
      x: 10,
      y: eyePositionY,
      width: 1,
      height: 2,
      type: 'rect',
      color: colors[colorValue][1]
    })
  }

  // Neck
  bot.neck.shapes.push({
    x: bot.neck.description === 'thin' ? 5 : 4,
    y: 4,
    width: bot.neck.description === 'thin' ? 2 : 4,
    height: 6,
    type: 'rect',
    color: colors[colorValue][1]
  })

  // Body is hard-coded so far
  bot.body.shapes.push({
    x: 2,
    y: 10,
    width: 8,
    height: 8,
    type: 'rect',
    color: colors[colorValue][0]
  })

  // Arms
  if (bot.arms.description === 'shoulder') {
    bot.arms.shapes.push({
      x: 2,
      y: 10,
      width: 2,
      height: 6,
      type: 'rect',
      color: colors[colorValue][1]
    })
    bot.arms.shapes.push({
      x: 8,
      y: 10,
      width: 2,
      height: 6,
      type: 'rect',
      color: colors[colorValue][1]
    })
  } else {
    bot.arms.shapes.push({
      type: 'polygon',
      points: '0,10 0,14 2,14 2,12 4,12 4,10 0,10',
      color: colors[colorValue][1]
    })
    bot.arms.shapes.push({
      type: 'polygon',
      points: '8,10 8,12 10,12 10,14 12,14 12,10 8,10',
      color: colors[colorValue][1]
    })
  }

  return bot
}

export const renderMessage = messageContent => {
  if (messageContent.includes('```') || messageContent.includes('**')) {
    // Only render MD if message contains markdown
    return DOMPurify.sanitize(marked.parse(aMessage))
  }
  // okay, let's cooperate with the newlines
  return messageContent.replaceAll('\n', '<br/>')
}

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