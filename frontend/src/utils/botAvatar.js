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
  bot.head.description = headValue === 0 ? 'low' : headValue === 1 ? 'high' : headValue === 2 ? 'narrow-chin' : 'wide-chin'
  bot.eyes.description = eyesValue === 0 ? 'round' : eyesValue === 1 ? 'square' : eyesValue === 2 ? 'rect' : eyesValue === 3 ? 'wink' : 'diamond'
  bot.hair.description = hairValue === 0 ? 'absent' : hairValue === 1 ? 'flat' : hairValue === 2 ? 'scruffy' : 'slick'
  bot.ears.description = earsValue === 0 ? 'absent' : earsValue === 1 ? 'large' : 'small'
  bot.arms.description = armsValue === 0 ? 'straight' : armsValue === 1 ? 'shoulder' : 'up'
  bot.neck.description = neckValue === 0 ? 'thick' : neckValue === 1 ? 'thin' : 'accordion'

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
  } else if (bot.hair.description === 'slick') {
    bot.hair.shapes.push({
      type: 'polygon',
      points: '2,0 10,0 10,2 9,1 8,1 7.8,0.2 7,1 3,1 2,2 2,0',
      color: colors[colorValue][1]
    })
  }

  // Head
  if (bot.head.description === 'narrow-chin') {
    bot.head.shapes.push({
      type: 'polygon',
      points: '2,0 10,0 10,6 6,8 2,6',
      color: colors[colorValue][0]
    })
  } else if (bot.head.description === 'wide-chin') {
    bot.head.shapes.push({
      type: 'polygon',
      points: '2,0 10,0 10,6 8,8 4,8 2,6',
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
  } else if (bot.eyes.description === 'diamond') {
    bot.eyes.shapes.push({
      type: 'polygon',
      points: bot.head.description === 'high' ? '3,2 4,1 5,2 4,3' : '3,4 4,3 5,4 4,5',
      color: colors[colorValue][1]
    })
    bot.eyes.shapes.push({
      type: 'polygon',
      points: bot.head.description === 'high' ? '7,2 8,1 9,2 8,3' : '7,4 8,3 9,4 8,5',
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
  if (bot.ears.description !== 'absent') {
    bot.ears.shapes.push({
      x: 1,
      y: eyePositionY,
      width: 1,
      height: bot.ears.description === 'large' ? 2 : 1,
      type: 'rect',
      color: colors[colorValue][1]
    })
    bot.ears.shapes.push({
      x: 10,
      y: eyePositionY,
      width: 1,
      height: bot.ears.description === 'large' ? 2 : 1,
      type: 'rect',
      color: colors[colorValue][1]
    })
  }

  // Neck
  if (bot.neck.description === 'accordion') {
    bot.neck.shapes.push({
      type: 'polygon',
      inverted_points: '4,10 5,9 4,8 5,7 4,6 5,5 4,4 8,4 7,5 8,6 7,7 8,8 7,9 8,10', // do these look better?
      points: '5,10 4,9 5,8 4,7 5,6 4,5 5,4 7,4 8,5 7,6 8,7 7,8 8,9 7,10',
      color: colors[colorValue][1]
    })
  } else {
    bot.neck.shapes.push({
      x: bot.neck.description === 'thin' ? 5 : 4,
      y: 4,
      width: bot.neck.description === 'thin' ? 2 : 4,
      height: 6,
      type: 'rect',
      color: colors[colorValue][1]
    })
  }

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
  } else if (bot.arms.description === 'straight') {
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
  } else {
    bot.arms.shapes.push({
      type: 'polygon',
      points: '4,10 2,6 0,7 2,11 3,11',
      color: colors[colorValue][1]
    })
    bot.arms.shapes.push({
      type: 'polygon',
      points: '8,10 10,6 12,7 10,11 9,11',
      color: colors[colorValue][1]
    })
  }

  return bot
}