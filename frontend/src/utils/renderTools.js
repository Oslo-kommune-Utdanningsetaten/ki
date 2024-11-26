import { marked } from 'marked'
import katex from 'katex'

export const fixFaultyKatex = (input) => {
  // Fix state indicators by removing subscript brackets around them
  let result = input.replace(/_\{(\(s\)|\(aq\)|\(l\)|\(g\))\}/g, " $1")
  // Fix double subscripts (e.g., `_4_{...}`) by keeping only the valid chemical subscript
  return result.replace(/_([0-9]+)_\{[^}]+\}/g, "_$1")
}

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
  return marked.parse(processedText)
}

export const renderKatex = messageContent => {
  const inlineMathRegex = /\\\((.+?)\\\)/g
  const blockMathRegex = /\\\[(.+?)\\\]/gs
  const renderedMathItems = {}
  let placeholderIndex = 0

  // sometimes the chatbot will generate double subscripts, which KaTeX doesn't like
  let processedText = fixFaultyKatex(messageContent)

  // Render block math items and add to renderedMathItems
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

  // Render inline math items and add to renderedMathItems
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

  // Replace placeholders with rendered math
  Object.keys(renderedMathItems).forEach((placeholderKey) => {
    const renderedMath = renderedMathItems[placeholderKey]
    processedText = processedText.replace(placeholderKey, renderedMath)
  })

  return processedText
}
