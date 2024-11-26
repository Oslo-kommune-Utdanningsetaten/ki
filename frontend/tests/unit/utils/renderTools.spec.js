import { getPlaceholderAt, renderMessage } from '../../../src/utils/renderTools.js'

test('ensures placeholder logic is working', () => {
  expect(getPlaceholderAt(2)).toBe('MATHPLACEHOLDER00002')
})
