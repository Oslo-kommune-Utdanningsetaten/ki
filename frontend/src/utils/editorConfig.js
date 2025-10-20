import {
  Bold,
  Essentials,
  Heading,
  Image,
  ImageBlock,
  ImageCaption,
  ImageInline,
  ImageResize,
  ImageStyle,
  ImageToolbar,
  ImageUpload,
  Indent,
  IndentBlock,
  Italic,
  Link,
  List,
  MediaEmbed,
  Paragraph,
  SimpleUploadAdapter,
} from 'ckeditor5'
import sanitizeHtml from 'sanitize-html'

export const SanitizeConfig = {
  allowedTags: sanitizeHtml.defaults.allowedTags.concat(['iframe', 'img']),
  allowedAttributes: {
    div: ['class'],
    figure: ['class', 'style'],
    p: ['style'],
    iframe: ['src', 'allow', 'allowfullscreen', 'class'],
    img: ['src', 'alt', 'style', 'class', 'width', 'height'],
    h2: ['style'],
    a: ['href', 'name', 'target'],
  },
}

export const editorConfig = {
  plugins: [
    Essentials,
    Bold,
    Italic,
    Link,
    List,
    Indent,
    IndentBlock,
    Paragraph,
    Heading,
    Image,
    ImageBlock,
    ImageInline,
    ImageUpload,
    ImageCaption,
    ImageResize,
    ImageStyle,
    ImageToolbar,
    SimpleUploadAdapter,
    MediaEmbed,
  ],
  toolbar: [
    'heading',
    '|',
    'bold',
    'italic',
    'link',
    '|',
    'bulletedList',
    'numberedList',
    'outdent',
    'indent',
    '|',
    'undo',
    'redo',
    '|',
    'insertImage',
    'mediaEmbed',
  ],
  image: {
    toolbar: [
      'imageStyle:alignLeft',
      'imageStyle:alignCenter',
      'imageStyle:alignRight',
      '|',
      'toggleImageCaption',
      'imageTextAlternative',
    ],
    insert: {
      integrations: ['upload'],
    },
  },
  link: {
    decorators: {
      openInNewTab: {
        mode: 'manual',
        label: 'Open in a new tab',
        defaultValue: true,
        attributes: {
          target: '_blank',
        },
      },
    },
  },
  simpleUpload: {
    uploadUrl: '/api/upload_info_image',
    withCredentials: false,
  },
  mediaEmbed: {
    // Only support for vimeo
    removeProviders: [
      'dailymotion',
      'spotify',
      'youtube',
      'instagram',
      'twitter',
      'googleMaps',
      'flickr',
      'facebook',
    ],
  },
  licenseKey: 'GPL',
}

export const createHtmlContent = content => {
  const parser = new DOMParser()
  const doc = parser.parseFromString(content || '', 'text/html')

  const oembeds = doc.querySelectorAll('oembed[url*="vimeo.com"]')

  oembeds.forEach(oembed => {
    let iframeSrc = oembed.getAttribute('url')
    const oembedParent = oembed.parentNode
    if (!iframeSrc || !oembedParent) return

    iframeSrc = iframeSrc.split('?')[0] // Remove query params

    const iframeSrcTokens = iframeSrc.split('/')
    // Video is unlisted if second to last token is a number as the format is:
    // Unlisted: <vimeo-url>/video_id/unlisted_hash
    // Listed: <vimeo-url>/video_id
    const isUnlisted = !isNaN(Number(iframeSrcTokens.at(-2)))

    const iframe = doc.createElement('iframe')

    if (isUnlisted) {
      const unlistedHash = iframeSrcTokens.pop()
      const videoId = iframeSrcTokens.pop()
      iframe.src = 'https://player.vimeo.com/video/' + videoId + '?h=' + unlistedHash
    } else {
      const videoId = iframeSrcTokens.pop()
      iframe.src = 'https://player.vimeo.com/video/' + videoId
    }

    iframe.allow = 'autoplay; fullscreen; picture-in-picture'
    iframe.allowFullscreen = true
    iframe.className = 'embed-responsive-item'

    const div = doc.createElement('div')
    div.className = 'ratio ratio-16x9'
    div.appendChild(iframe)

    oembedParent.replaceChild(div, oembed)
  })

  return sanitizeHtml(doc.body.innerHTML, SanitizeConfig)
}
