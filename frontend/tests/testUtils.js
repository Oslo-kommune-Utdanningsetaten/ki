// We dont care about exact formatting, just that the html is correct
// Therefore, get rid of comments, newlines and extra spaces
export const sanitizeHtml = (html) => {
  return html
    .replace(/<\!--.*?-->/g, "")
    .split('\n')
    .map(line => line.trim())
    .join('')
}