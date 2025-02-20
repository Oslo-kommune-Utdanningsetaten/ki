// Each entry in the bodyColorCombinations array is a pair of colors used in the bot avatar
const bodyColorCombinations = [
  ['oslo-fill-blue', 'oslo-fill-dark-blue'],
  ['oslo-fill-yellow', 'oslo-fill-black'],
  ['oslo-fill-green', 'oslo-fill-dark-green'],
  ['oslo-fill-red', 'oslo-fill-black'],
  ['oslo-fill-dark-beige', 'oslo-fill-black'],
]

export const bodyColors = [
  { id: 0, code: 'oslo-fill-blue', text: 'Blå' },
  { id: 1, code: 'oslo-fill-yellow', text: 'Gul' },
  { id: 2, code: 'oslo-fill-green', text: 'Grønn' },
  { id: 3, code: 'oslo-fill-red', text: 'Rød' },
  { id: 4, code: 'oslo-fill-dark-beige', text: 'Grå' },
]

export const hairColors = [
  { id: 0, code: 'oslo-fill-black', text: 'Svart' },
  { id: 1, code: 'oslo-fill-yellow', text: 'Gul' },
  { id: 2, code: 'oslo-fill-red', text: 'Rød' },
  { id: 3, code: 'oslo-fill-dark-beige', text: 'Grå' },
  { id: 4, code: 'oslo-fill-blue', text: 'Blå' },
  { id: 5, code: 'oslo-fill-dark-blue', text: 'Mørk blå' },
  { id: 6, code: 'oslo-fill-green', text: 'Grønn' },
  { id: 7, code: 'oslo-fill-dark-green', text: 'Mørk grønn' },
]

export const defaultAvatarScheme = [0, 0, 0, 0, 0, 0, 0, 0]
const expectedAvatarSchemeLength = defaultAvatarScheme.length

// Takes an array of values, where each describes a body part of the bot avatar
// Returns an object where the various parts are described in detail
export const createBotDescriptionFromScheme = (scheme) => {
  const avatarScheme = scheme || defaultAvatarScheme
  // Pad the array if it's too short
  while (avatarScheme.length < expectedAvatarSchemeLength) {
    avatarScheme.push(0)
  }
  const [bodyColorCombinationIdex, headIndex, eyesIndex, hairIndex, earsIndex, armsIndex, neckIndex, hairColorIndex] = avatarScheme

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
  bot.head.description = headIndex === 0 ? 'low' : headIndex === 1 ? 'high' : headIndex === 2 ? 'narrow-chin' : 'wide-chin'
  bot.eyes.description = eyesIndex === 0 ? 'round' : eyesIndex === 1 ? 'square' : eyesIndex === 2 ? 'rect' : eyesIndex === 3 ? 'wink' : eyesIndex === 4 ? 'diamond' : 'triangle'
  bot.hair.description = hairIndex === 0 ? 'absent' : hairIndex === 1 ? 'flat' : hairIndex === 2 ? 'scruffy' : 'slick'
  bot.ears.description = earsIndex === 0 ? 'absent' : earsIndex === 1 ? 'large' : 'small'
  bot.arms.description = armsIndex === 0 ? 'straight' : armsIndex === 1 ? 'shoulder' : 'up'
  bot.neck.description = neckIndex === 0 ? 'thick' : neckIndex === 1 ? 'thin' : 'accordion'

  const primaryBodyColor = bodyColorCombinations[bodyColorCombinationIdex][0]
  const secondaryBodyColor = bodyColorCombinations[bodyColorCombinationIdex][1]
  const hairColor = hairColors[hairColorIndex].code

  // Hair
  if (bot.hair.description === 'flat') {
    bot.hair.shapes.push({
      x: 2,
      y: 0,
      width: 8,
      height: 2,
      type: 'rect',
      color: hairColor
    })
  } else if (bot.hair.description === 'scruffy') {
    bot.hair.shapes.push({
      type: 'polygon',
      points: '2,0 10,0 10,2 9,2 9,1 8,1 8,2 6,2 6,1 5,1 5,2 4,2 4,1 3,1 3,2 2,2 2,0',
      color: hairColor
    })
  } else if (bot.hair.description === 'slick') {
    bot.hair.shapes.push({
      type: 'polygon',
      points: '2,0 10,0 10,2 9,1 8,1 7.8,0.2 7,1 3,1 2,2 2,0',
      color: hairColor
    })
  }

  // Head
  if (bot.head.description === 'narrow-chin') {
    bot.head.shapes.push({
      type: 'polygon',
      points: '2,0 10,0 10,6 6,8 2,6',
      color: primaryBodyColor
    })
  } else if (bot.head.description === 'wide-chin') {
    bot.head.shapes.push({
      type: 'polygon',
      points: '2,0 10,0 10,6 8,8 4,8 2,6',
      color: primaryBodyColor
    })
  } else {
    bot.head.shapes.push({
      x: 2,
      y: 0,
      width: 8,
      height: bot.head.description === 'high' ? 4 : 8,
      type: 'rect',
      color: primaryBodyColor
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
      color: secondaryBodyColor
    })
    bot.eyes.shapes.push({
      x: 7,
      y: eyePositionY,
      width: 2,
      height: 2,
      type: 'rect',
      color: secondaryBodyColor
    })
  } else if (bot.eyes.description === 'wink') {
    bot.eyes.shapes.push({
      x: 3,
      y: eyePositionY,
      width: 2,
      height: 2,
      type: 'rect',
      color: secondaryBodyColor
    })
    bot.eyes.shapes.push({
      x: 7,
      y: eyePositionY,
      width: 2,
      height: 1,
      type: 'rect',
      color: secondaryBodyColor
    })
  } else if (bot.eyes.description === 'diamond') {
    bot.eyes.shapes.push({
      type: 'polygon',
      points: bot.head.description === 'high' ? '3,2 4,1 5,2 4,3' : '3,4 4,3 5,4 4,5',
      color: secondaryBodyColor
    })
    bot.eyes.shapes.push({
      type: 'polygon',
      points: bot.head.description === 'high' ? '7,2 8,1 9,2 8,3' : '7,4 8,3 9,4 8,5',
      color: secondaryBodyColor
    })
  } else if (bot.eyes.description === 'triangle') {
    bot.eyes.shapes.push({
      type: 'polygon',
      points: bot.head.description === 'high' ? '3,2 4,1 5,2' : '3,4 4,3 5,4',
      color: secondaryBodyColor
    })
    bot.eyes.shapes.push({
      type: 'polygon',
      points: bot.head.description === 'high' ? '7,2 8,1 9,2' : '7,4 8,3 9,4',
      color: secondaryBodyColor
    })
  } else if (bot.eyes.description === 'rect') {
    bot.eyes.shapes.push({
      x: 3,
      y: eyePositionY,
      width: 2,
      height: 1,
      type: 'rect',
      color: secondaryBodyColor
    })
    bot.eyes.shapes.push({
      x: 7,
      y: eyePositionY,
      width: 2,
      height: 1,
      type: 'rect',
      color: secondaryBodyColor
    })
  } else {
    bot.eyes.shapes.push({
      type: 'circle',
      cx: 4,
      cy: eyePositionY + 1,
      r: 1,
      color: secondaryBodyColor
    })
    bot.eyes.shapes.push({
      type: 'circle',
      cx: 8,
      cy: eyePositionY + 1,
      r: 1,
      color: secondaryBodyColor
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
      color: secondaryBodyColor
    })
    bot.ears.shapes.push({
      x: 10,
      y: eyePositionY,
      width: 1,
      height: bot.ears.description === 'large' ? 2 : 1,
      type: 'rect',
      color: secondaryBodyColor
    })
  }

  // Neck
  if (bot.neck.description === 'accordion') {
    bot.neck.shapes.push({
      type: 'polygon',
      inverted_points: '4,10 5,9 4,8 5,7 4,6 5,5 4,4 8,4 7,5 8,6 7,7 8,8 7,9 8,10', // do these look better?
      points: '5,10 4,9 5,8 4,7 5,6 4,5 5,4 7,4 8,5 7,6 8,7 7,8 8,9 7,10',
      color: secondaryBodyColor
    })
  } else {
    bot.neck.shapes.push({
      x: bot.neck.description === 'thin' ? 5 : 4,
      y: 4,
      width: bot.neck.description === 'thin' ? 2 : 4,
      height: 6,
      type: 'rect',
      color: secondaryBodyColor
    })
  }

  // Body is hard-coded so far
  bot.body.shapes.push({
    x: 2,
    y: 10,
    width: 8,
    height: 8,
    type: 'rect',
    color: primaryBodyColor
  })

  // Arms
  if (bot.arms.description === 'shoulder') {
    bot.arms.shapes.push({
      x: 2,
      y: 10,
      width: 2,
      height: 6,
      type: 'rect',
      color: secondaryBodyColor
    })
    bot.arms.shapes.push({
      x: 8,
      y: 10,
      width: 2,
      height: 6,
      type: 'rect',
      color: secondaryBodyColor
    })
  } else if (bot.arms.description === 'straight') {
    bot.arms.shapes.push({
      type: 'polygon',
      points: '0,10 0,14 2,14 2,12 4,12 4,10 0,10',
      color: secondaryBodyColor
    })
    bot.arms.shapes.push({
      type: 'polygon',
      points: '8,10 8,12 10,12 10,14 12,14 12,10 8,10',
      color: secondaryBodyColor
    })
  } else {
    bot.arms.shapes.push({
      type: 'polygon',
      points: '4,10 2,6 0,7 2,11 3,11',
      color: secondaryBodyColor
    })
    bot.arms.shapes.push({
      type: 'polygon',
      points: '8,10 10,6 12,7 10,11 9,11',
      color: secondaryBodyColor
    })
  }

  return bot
}