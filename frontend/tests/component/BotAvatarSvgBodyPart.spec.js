import { mount } from '@vue/test-utils'
import BotAvatarSvgBodyPart from '../../src/components/BotAvatarSvgBodyPart.vue'
import { sanitizeHtml } from '../testUtils.js'

test('ensures eyes are rendered correctly', () => {
  const bodyPartProps = {
    description: "rect",
    shapes: [
      { x: 3, y: 1, width: 2, color: "oslo-fill-dark-green", height: 1, type: "rect" },
      { x: 7, y: 1, width: 2, color: "oslo-fill-dark-green", height: 1, type: "rect" }
    ]
  }

  const wrapper = mount(BotAvatarSvgBodyPart, { props: { bodyPart: bodyPartProps } })
  const expected = `
  <g><rect class="oslo-fill-dark-green" x="3" y="1" width="2" height="1"></rect></g>
  <g><rect class="oslo-fill-dark-green" x="7" y="1" width="2" height="1"></rect></g>
  `
  const result = sanitizeHtml(wrapper.html())
  expect(result).toBe(sanitizeHtml(expected))
})

