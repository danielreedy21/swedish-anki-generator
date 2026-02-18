const { contextBridge, ipcRenderer } = require('electron')

// expose a clean API to the React app
// the renderer can call window.api.lookupWord('hund') etc.
contextBridge.exposeInMainWorld('api', {

  // called by main process when hotkey fires with clipboard content
  onLookupWord: (callback) => {
    ipcRenderer.on('lookup-word', (_, word) => callback(word))
    // return cleanup function
    return () => ipcRenderer.removeAllListeners('lookup-word')
  },

  // called by React app for manual search bar lookups
  lookupWord: (word) =>
    ipcRenderer.invoke('lookup-word', word),

  getImages: (word) =>
    ipcRenderer.invoke('get-images', word),

  getAudio: (word) =>
    ipcRenderer.invoke('get-audio', word),

  improveTranslation: (word, definitionIndex) =>
    ipcRenderer.invoke('improve-translation', word, definitionIndex),

  createCard: (cardData) =>
    ipcRenderer.invoke('create-card', cardData),

  getDecks: () =>
    ipcRenderer.invoke('get-decks'),

  hideWindow: () =>
    ipcRenderer.send('hide-window'),

  playAudio: (filePath) =>
    ipcRenderer.send('play-audio', filePath),
})