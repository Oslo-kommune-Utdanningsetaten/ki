export const getPreferences = () => {
  const preferences = localStorage.getItem('preferences')
  return preferences ? JSON.parse(preferences) : {}
}

export const setPreferences = (key, value) => {
  const currentPreferences = getPreferences()
  const preferences = Object.assign({}, currentPreferences, { [key]: value })
  localStorage.setItem('preferences', JSON.stringify(preferences))
}

export const clearPreferences = () => {
  localStorage.removeItem('preferences')
}
