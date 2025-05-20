import { mount } from '@vue/test-utils'
import BotAvatar from '../../src/components/BotAvatar.vue'
import { sanitizeHtml } from '../testUtils.js'

test('renders a bot avatar correctly based on scheme', () => {
  const avatarScheme = [3, 1, 0, 0, 0, 1, 1]

  const wrapper = mount(BotAvatar, { props: { avatarScheme: avatarScheme } })
  const expected = `
  <div hidden="">[3,1,0,0,0,1,1,0]</div>
  <svg viewBox="0 0 12 18">
    <g><rect class="oslo-fill-black" x="5" y="4" width="2" height="6"></rect></g><g><rect class="oslo-fill-red" x="2" y="0" width="8" height="4"></rect></g><g><rect class="oslo-fill-red" x="2" y="10" width="8" height="8"></rect></g><g><circle class="oslo-fill-black" cx="4" cy="2" r="1"></circle></g><g><circle class="oslo-fill-black" cx="8" cy="2" r="1"></circle></g><g><rect class="oslo-fill-black" x="2" y="10" width="2" height="6"></rect></g><g><rect class="oslo-fill-black" x="8" y="10" width="2" height="6"></rect></g>
  </svg>
`
  const result = sanitizeHtml(wrapper.html())
  expect(result).toContain(sanitizeHtml(expected))
})
