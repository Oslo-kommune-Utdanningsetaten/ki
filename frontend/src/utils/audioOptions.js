import { getPreferences, setPreferences } from './localstorageTools.js'

export const speechRates = [
  { name: 'slow', title: 'Sakte', value: "-15.00%" },
  { name: 'normal', title: 'Vanlig', value: "+10.00%" },
]
const defaultLanguage = 'nb-NO'
const defaultSpeechRate = speechRates[1]

export const getSelectedLanguage = () => {
  const { selectedLanguage } = getPreferences()
  return selectedLanguage || defaultLanguage
}

export const getSelectedVoice = (language) => {
  const { selectedVoices } = getPreferences()
  const voice = selectedVoices ? selectedVoices[language] : null
  return voice || getVoicesForLanguage(language)[0].code
}

export const getSelectedSpeechRate = () => {
  const { selectedSpeechRate } = getPreferences()
  return selectedSpeechRate || defaultSpeechRate
}

export const getVoicesForLanguage = (language) => {
  return languageOptions.languages.find((lang) => lang.code === language).voices
}

export const updateLanguagePreferences = (options = {}) => {
  let { selectedLanguage, selectedVoice, selectedSpeechRate } = options

  // Update language
  selectedLanguage = selectedLanguage || getSelectedLanguage()
  setPreferences('selectedLanguage', selectedLanguage)

  // Update speech rate
  selectedSpeechRate = selectedSpeechRate || getSelectedSpeechRate()
  setPreferences('selectedSpeechRate', selectedSpeechRate)

  // Update voice
  if (!getVoicesForLanguage(selectedLanguage).find((voice) => voice.code === selectedVoice)) {
    selectedVoice = getSelectedVoice(selectedLanguage)
  }
  // Voice is valid, now merge with existing preferences
  const { selectedVoices } = getPreferences()
  const updatedSelection = Object.assign({}, selectedVoices, { [selectedLanguage]: selectedVoice })
  setPreferences('selectedVoices', updatedSelection)
}


export const languageOptions = {
  languages: [
    {
      name: 'Norsk',
      code: 'nb-NO',
      voices: [
        { name: 'Pernille', code: 'nb-NO-PernilleNeural' },
        { name: 'Finn', code: 'nb-NO-FinnNeural' },
        { name: 'Iselin', code: 'nb-NO-IselinNeural' },
      ],
    },
    {
      name: 'English (US)',
      code: 'en-US',
      voices: [
        { name: 'Ava', code: 'en-US-AvaMultilingualNeural' },
        { name: 'Andrew', code: 'en-US-AndrewMultilingualNeural' },
        { name: 'Emma', code: 'en-US-EmmaMultilingualNeural' },
        { name: 'Brian', code: 'en-US-BrianMultilingualNeural' },
        { name: 'Ana 👶', code: 'en-US-AnaNeural' },
      ],
    },
    {
      name: 'English (UK)',
      code: 'en-GB',
      voices: [
        { name: 'Sonia', code: 'en-GB-SoniaNeural' },
        { name: 'Ryan', code: 'en-GB-RyanNeural' },
        { name: 'Alfie', code: 'en-GB-AlfieNeural' },
        { name: 'Olivia', code: 'en-GB-OliviaNeural' },
        { name: 'Maisie 👶', code: 'en-GB-MaisieNeural' },
      ],
    },
    {
      name: 'Espanol',
      code: 'es-ES',
      voices: [
        { name: 'Elvira', code: 'es-ES-ElviraNeural' },
        { name: 'Alvaro', code: 'es-ES-AlvaroNeural' },
        { name: 'Abril', code: 'es-ES-AbrilNeural' },
        { name: 'Dario', code: 'es-ES-DarioNeural' },
      ],
    },
    {
      name: 'Français',
      code: 'fr-FR',
      voices: [
        { name: 'Denise', code: 'fr-FR-DeniseNeural' },
        { name: 'Henri', code: 'fr-FR-HenriNeural' },
        { name: 'Alain', code: 'fr-FR-AlainNeural' },
        { name: 'Brigitte', code: 'fr-FR-BrigitteNeural' },
      ],
    },
    {
      name: 'Deutsch',
      code: 'de-DE',
      voices: [
        { name: 'Katja', code: 'de-DE-KatjaNeural' },
        { name: 'Conrad', code: 'de-DE-ConradNeural' },
        { name: 'Klaus', code: 'de-DE-KlausNeural' },
        { name: 'Amala', code: 'de-DE-AmalaNeural' },
      ],
    },
  ],
}