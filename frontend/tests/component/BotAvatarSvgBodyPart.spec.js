import { mount } from '@vue/test-utils'
import BotAvatarSvgBodyPart from '../../src/components/BotAvatarSvgBodyPart.vue'

// We dont care about exact formatting, just that the html is correct
// Therefore, get rid of newlines and extra spaces
const sanitizeHtml = (html) => html.split('\n').map(line => line.trim()).join('')

test('ensures eyes are rendered correctly', () => {
  const bodyPartProps = {
    description: "rect",
    shapes: [
      { x: 3, y: 1, width: 2, color: "oslo-fill-dark-green", height: 1, type: "rect" },
      { x: 7, y: 1, width: 2, color: "oslo-fill-dark-green", height: 1, type: "rect" }
    ]
  }

  const wrapper = mount(BotAvatarSvgBodyPart, { props: { bodyPart: bodyPartProps } })
  const expectedEyes = `
  <g><rect class="oslo-fill-dark-green" x="3" y="1" width="2" height="1"></rect></g>
  <g><rect class="oslo-fill-dark-green" x="7" y="1" width="2" height="1"></rect></g>
  `
  const html = wrapper.html().split('\n').map(line => line.trim()).join('')
  expect(sanitizeHtml(html)).toContain(sanitizeHtml(expectedEyes))
})

