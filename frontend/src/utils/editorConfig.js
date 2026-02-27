import {
  Bold,
  Essentials,
  Heading,
  Image,
  ImageBlock,
  ImageCaption,
  ImageInline,
  ImageInsert,
  ImageResize,
  ImageStyle,
  ImageTextAlternative,
  ImageToolbar,
  ImageUpload,
  Indent,
  IndentBlock,
  Italic,
  Link,
  LinkImage,
  List,
  MediaEmbed,
  Paragraph,
  SimpleUploadAdapter,
  HorizontalLine,
} from 'ckeditor5'
import sanitizeHtml from 'sanitize-html'

export const sanitizeConfig = {
  allowedTags: sanitizeHtml.defaults.allowedTags.concat(['iframe', 'img']),
  allowedAttributes: {
    div: ['class'],
    figure: ['class', 'style'],
    p: ['style'],
    iframe: ['src', 'allow', 'allowfullscreen', 'class'],
    img: ['src', 'alt', 'style', 'class', 'title'],
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
    LinkImage,
    List,
    Indent,
    IndentBlock,
    Paragraph,
    Heading,
    Image,
    ImageBlock,
    ImageInline,
    ImageInsert,
    ImageUpload,
    ImageCaption,
    ImageResize,
    ImageStyle,
    ImageTextAlternative,
    ImageToolbar,
    HorizontalLine,
    SimpleUploadAdapter,
    MediaEmbed,
  ],
  toolbar: [
    'undo',
    'redo',
    '|',
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
    'horizontalLine',
    'insertImage',
    'mediaEmbed',
  ],
  heading: {
    options: [
      { model: 'paragraph', title: 'Paragraph', class: 'ck-heading_paragraph' },
      { model: 'heading2', view: 'h2', title: 'Heading 2', class: 'ck-heading_heading2' },
      { model: 'heading3', view: 'h3', title: 'Heading 3', class: 'ck-heading_heading3' },
      { model: 'heading4', view: 'h4', title: 'Heading 4', class: 'ck-heading_heading4' },
      { model: 'heading5', view: 'h5', title: 'Heading 5', class: 'ck-heading_heading5' },
      { model: 'heading6', view: 'h6', title: 'Heading 6', class: 'ck-heading_heading6' },
    ],
  },
  image: {
    toolbar: [
      'imageStyle:inline',
      'imageStyle:alignLeft',
      'imageStyle:alignCenter',
      'imageStyle:alignRight',
      'imageResize',
      '|',
      'toggleImageCaption',
      'imageTextAlternative',
      '|',
      'linkImage',
    ],
    insert: {
      integrations: ['upload', 'url'],
      type: 'inline',
    },
    upload: {
      types: ['jpeg', 'png', 'gif', 'bmp', 'svg'],
    },
    styles: ['inline', 'block', 'alignLeft', 'alignCenter', 'alignRight'],
    resizeOptions: [
      {
        name: 'resizeImage:original',
        label: 'Original',
        value: null,
      },
      {
        name: 'resizeImage:20px',
        label: '20px',
        value: '20',
      },
      {
        name: 'resizeImage:50px',
        label: '50px',
        value: '50',
      },
    ],
    resizeUnit: 'px', // or 'px' for pixel-based sizing
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
    uploadUrl: '/api/upload_info_file',
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

  return sanitizeHtml(doc.body.innerHTML, sanitizeConfig)
}
