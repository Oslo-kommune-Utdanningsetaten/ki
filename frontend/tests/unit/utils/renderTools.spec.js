import { getPlaceholderAt, renderMessage, renderKatex, fixDoubleSubscripts } from '../../../src/utils/renderTools.js'
import { sanitizeHtml } from '../../testUtils.js'

test('creates correct placeholder', () => {
  expect(getPlaceholderAt(2)).toBe('MATHPLACEHOLDER00002')
})

test('renders markdown', () => {
  const result = renderMessage('# Hello world', { useKatex: false })
  const expected = '<h1>Hello world</h1>\n'
  expect(result).toBe(expected)
})

test('renders katex', () => {
  const input = String.raw`
\( \text{Cu}^{2+} (aq) + \text{Fe} (s) \rightarrow \text{Cu} (s) + \text{Fe}^{2+} (aq) \)
`
  const result = renderKatex(input)
  const expected = String.raw`<span class="katex"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msup><mtext>Cu</mtext><mrow><mn>2</mn><mo>+</mo></mrow></msup><mo stretchy="false">(</mo><mi>a</mi><mi>q</mi><mo stretchy="false">)</mo><mo>+</mo><mtext>Fe</mtext><mo stretchy="false">(</mo><mi>s</mi><mo stretchy="false">)</mo><mo>→</mo><mtext>Cu</mtext><mo stretchy="false">(</mo><mi>s</mi><mo stretchy="false">)</mo><mo>+</mo><msup><mtext>Fe</mtext><mrow><mn>2</mn><mo>+</mo></mrow></msup><mo stretchy="false">(</mo><mi>a</mi><mi>q</mi><mo stretchy="false">)</mo></mrow><annotation encoding="application/x-tex"> \text{Cu}^{2+} (aq) + \text{Fe} (s) \rightarrow \text{Cu} (s) + \text{Fe}^{2+} (aq) </annotation></semantics></math></span>`
  expect(sanitizeHtml(result)).toBe(sanitizeHtml(expected))
})

test('fixes katex code with double subscript', () => {
  const input = String.raw`Fe_{(s)} + CuSO_4_{(aq)} \rightarrow FeSO_4_{(aq)} + Cu_{(s)}`
  const result = fixDoubleSubscripts(input)
  const expected = String.raw`Fe_{(s)} + CuSO_{4(aq)} \rightarrow FeSO_{4(aq)} + Cu_{(s)}`
  expect(result).toBe(expected)
})


test('renders katex code with double subscript', () => {
  const input = String.raw`
\[ 
Fe_{(s)} + CuSO_4_{(aq)} \rightarrow FeSO_4_{(aq)} + Cu_{(s)}
\]
`
  const result = renderKatex(input)
  const expected = String.raw`<span class="katex"><math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><semantics><mrow><mi>F</mi><msub><mi>e</mi><mrow><mo stretchy="false">(</mo><mi>s</mi><mo stretchy="false">)</mo></mrow></msub><mo>+</mo><mi>C</mi><mi>u</mi><mi>S</mi><msub><mi>O</mi><mrow><mn>4</mn><mo stretchy="false">(</mo><mi>a</mi><mi>q</mi><mo stretchy="false">)</mo></mrow></msub><mo>→</mo><mi>F</mi><mi>e</mi><mi>S</mi><msub><mi>O</mi><mrow><mn>4</mn><mo stretchy="false">(</mo><mi>a</mi><mi>q</mi><mo stretchy="false">)</mo></mrow></msub><mo>+</mo><mi>C</mi><msub><mi>u</mi><mrow><mo stretchy="false">(</mo><mi>s</mi><mo stretchy="false">)</mo></mrow></msub></mrow><annotation encoding="application/x-tex">Fe_{(s)} + CuSO_{4(aq)} \rightarrow FeSO_{4(aq)} + Cu_{(s)}
</annotation></semantics></math></span>`
  expect(sanitizeHtml(result)).toBe(sanitizeHtml(expected))
})


test('renders a message with a mix of katext and markdown', () => {
  const input = String.raw`**Reaksjonsligning:**

\( \text{Cu}^{2+} (aq) + \text{Fe} (s) \rightarrow \text{Cu} (s) + \text{Fe}^{2+} (aq) \)

### Trinn for utførelsen`
  const result = renderMessage(input, { useKatex: true })
  const expected = String.raw`<p><strong>Reaksjonsligning:</strong></p>
<p><span class="katex"><math xmlns="http://www.w3.org/1998/Math/MathML"><semantics><mrow><msup><mtext>Cu</mtext><mrow><mn>2</mn><mo>+</mo></mrow></msup><mo stretchy="false">(</mo><mi>a</mi><mi>q</mi><mo stretchy="false">)</mo><mo>+</mo><mtext>Fe</mtext><mo stretchy="false">(</mo><mi>s</mi><mo stretchy="false">)</mo><mo>→</mo><mtext>Cu</mtext><mo stretchy="false">(</mo><mi>s</mi><mo stretchy="false">)</mo><mo>+</mo><msup><mtext>Fe</mtext><mrow><mn>2</mn><mo>+</mo></mrow></msup><mo stretchy="false">(</mo><mi>a</mi><mi>q</mi><mo stretchy="false">)</mo></mrow><annotation encoding="application/x-tex"> \text{Cu}^{2+} (aq) + \text{Fe} (s) \rightarrow \text{Cu} (s) + \text{Fe}^{2+} (aq) </annotation></semantics></math></span></p>
<h3>Trinn for utførelsen</h3>`
  expect(sanitizeHtml(result)).toBe(sanitizeHtml(expected))
})

