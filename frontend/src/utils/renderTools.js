import { marked } from 'marked'
import katex from 'katex'


export const getPlaceholderAt = (placeholderIndex) => {
  const paddedIndex = placeholderIndex.toString().padStart(5, '0')
  return `MATHPLACEHOLDER${paddedIndex}`
}

export const renderMessage = (messageContent, options = { useKatex: true }) => {
  const { useKatex } = options
  let processedText = messageContent
  if (useKatex) {
    processedText = renderKatex(processedText)
  }
  return marked.parse(messageContent)
}

export const renderKatex = messageContent => {
  const inlineMathRegex = /\\\((.+?)\\\)/g
  const blockMathRegex = /\\\[(.+?)\\\]/gs
  const renderedMathItems = {}
  let processedText = messageContent
  let placeholderIndex = 0

  // Process block math first
  processedText = processedText.replace(blockMathRegex, (_, math) => {
    try {
      const renderedMath = katex.renderToString(math, {
        output: 'mathml',
        throwOnError: false,
        displayMode: true,
      })
      const placeholderKey = getPlaceholderAt(placeholderIndex)
      renderedMathItems[placeholderKey] = renderedMath
      placeholderIndex++
      return placeholderKey
    } catch (err) {
      console.error("Katex block error:", err)
      return _
    }
  })

  // Process inline math
  processedText = processedText.replace(inlineMathRegex, (_, math) => {
    try {
      const renderedMath = katex.renderToString(math, {
        output: 'mathml',
        throwOnError: false,
        displayMode: false,
      })
      const placeholderKey = getPlaceholderAt(placeholderIndex)
      renderedMathItems[placeholderKey] = renderedMath
      placeholderIndex++
      return placeholderKey
    } catch (err) {
      console.error("Katex inline error:", err)
      return _
    }
  })

  Object.keys(renderedMathItems).forEach((placeholderKey) => {
    const renderedMath = renderedMathItems[placeholderKey]
    processedText = processedText.replace(placeholderKey, renderedMath)
  })

  return processedText
}
