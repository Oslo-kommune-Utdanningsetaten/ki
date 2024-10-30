// Takes an array of values, where each describes a body part of the bot
// Returns an object where the various parts are described in detail
export const createBotDescriptionFromScheme = (scheme) => {
  const [colorValue, headValue, eyesValue, hairValue, earsValue, armsValue, neckValue] = scheme && scheme.length === 7 ? scheme : [0, 0, 0, 0, 0, 0, 0]

  // Empty bot object
  // Each shape is implicitly a rectangle, unless type says otherwise
  const bot = {
    colors: [],
    hair: {},
    head: {},
    eyes: { shapes: [] },
    ears: { shapes: [] },
    neck: {},
    body: {},
    arms: { shapes: [] },
  }

  // Translate the values to human readable descriptions for easier reference
  bot.colors = colors[colorValue]
  bot.head.description = headValue === 1 ? 'high' : 'low'
  bot.eyes.description = eyesValue === 0 ? 'circle' : eyesValue === 1 ? 'rect' : 'wink'
  bot.hair.description = hairValue === 0 ? 'absent' : hairValue === 1 ? 'flat' : 'scruffy'
  bot.ears.description = earsValue === 1 ? 'present' : 'absent'
  bot.arms.description = armsValue === 1 ? 'present' : 'absent'
  bot.neck.description = neckValue === 1 ? 'thin' : 'thick'

  // Hair
  if (bot.hair.description === 'flat') {
    bot.hair.x = 2
    bot.hair.y = 0
    bot.hair.width = 8
    bot.hair.height = 2
  } else if (bot.hair.description === 'scruffy') {
    bot.hair.type = 'polygon'
    bot.hair.points = '2 0 10 0 10 2 9 2 9 1 8 1 8 2 6 2 6 1 5 1 5 2 4 2 4 1 3 1 3 2 2 2 2 0'
  }

  // Head
  bot.head.x = 2
  bot.head.y = 0
  bot.head.width = 8
  bot.head.height = bot.head.description === 'high' ? 4 : 8

  // Eyes
  const eyePositionY = bot.head.description === 'high' ? 1 : 3
  if (bot.eyes.description === 'rect') {
    bot.eyes.shapes.push({
      x: 3,
      y: eyePositionY,
      width: 2,
      height: 2,
    })
    bot.eyes.shapes.push({
      x: 7,
      y: eyePositionY,
      width: 2,
      height: 2,
    })
  } else if (bot.eyes.description === 'wink') {
    bot.eyes.shapes.push({
      x: 3,
      y: eyePositionY,
      width: 2,
      height: 2,
    })
    bot.eyes.shapes.push({
      x: 7,
      y: eyePositionY,
      width: 2,
      height: 1,
    })
  } else if (bot.eyes.description === 'circle') {
    bot.eyes.shapes.push({
      type: 'circle',
      cx: 4,
      cy: eyePositionY + 1,
      r: 1,
    })
    bot.eyes.shapes.push({
      type: 'circle',
      cx: 8,
      cy: eyePositionY + 1,
      r: 1,
    })
  }

  // Ears, same Y position as eyes
  if (bot.ears.description === 'present') {
    bot.ears.shapes.push({
      x: 1,
      y: eyePositionY,
      width: 1,
      height: 2,
    })
    bot.ears.shapes.push({
      x: 10,
      y: eyePositionY,
      width: 1,
      height: 2,
    })
  }

  // Neck
  bot.neck.x = bot.neck.description === 'thin' ? 5 : 4
  bot.neck.y = 4
  bot.neck.width = bot.neck.description === 'thin' ? 2 : 4
  bot.neck.height = 6

  // Body is hard-coded so far
  bot.body.x = 2
  bot.body.y = 10
  bot.body.width = 8
  bot.body.height = 8

  // Arms
  if (bot.arms.description === 'present') {
    bot.arms.shapes.push({
      x: 2,
      y: 10,
      width: 2,
      height: 6,
    })
    bot.arms.shapes.push({
      x: 8,
      y: 10,
      width: 2,
      height: 6,
    })
  } else {
    bot.arms.shapes.push({
      type: 'polygon',
      points: '0 10 0 14 2 14 2 12 4 12 4 10 0 10',
    })
    bot.arms.shapes.push({
      type: 'polygon',
      points: '8 10 8 12 10 12 10 14 12 14 12 10 8 10',
    })
  }

  return bot
}