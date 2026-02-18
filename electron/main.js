const { app, BrowserWindow, globalShortcut, clipboard, ipcMain, shell } = require('electron')
const path = require('path')

const FLASK_URL = 'http://127.0.0.1:5000'
const DEV_MODE = process.env.NODE_ENV === 'development'

let mainWindow = null

// ---------------------------------------------------------------------------
// Window
// ---------------------------------------------------------------------------

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 520,
    height: 700,
    show: false,               // start hidden — only show on hotkey
    resizable: true,
    titleBarStyle: 'hiddenInset', // native Mac look
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,  // security best practice
      nodeIntegration: false,
    },
  })

  // in dev, load from Vite dev server; in prod, load built files
  if (DEV_MODE) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools({ mode: 'detach' })
  } else {
    mainWindow.loadFile(path.join(__dirname, 'dist', 'index.html'))
  }

  // hide instead of close so it reappears instantly on next hotkey press
  mainWindow.on('close', (e) => {
    e.preventDefault()
    mainWindow.hide()
  })
}

// ---------------------------------------------------------------------------
// Global hotkey — Cmd+Shift+S
// ---------------------------------------------------------------------------

function registerHotkey() {
  const registered = globalShortcut.register('CommandOrControl+Shift+S', () => {
    const word = clipboard.readText().trim()

    if (!word) return

    if (mainWindow.isVisible()) {
      // if already open, just look up the new word
      mainWindow.webContents.send('lookup-word', word)
    } else {
      mainWindow.show()
      mainWindow.focus()
      // wait for window to be ready before sending
      mainWindow.webContents.send('lookup-word', word)
    }
  })

  if (!registered) {
    console.error('Failed to register global shortcut Cmd+Shift+S')
  }
}

// ---------------------------------------------------------------------------
// IPC handlers — called from the React app via window.api
// ---------------------------------------------------------------------------

// look up a word from the search bar (user typed it manually)
ipcMain.handle('lookup-word', async (_, word) => {
  const res = await fetch(`${FLASK_URL}/lookup/${encodeURIComponent(word)}`)
  if (!res.ok) return null
  return res.json()
})

// fetch images for a word
ipcMain.handle('get-images', async (_, word) => {
  const res = await fetch(`${FLASK_URL}/images/${encodeURIComponent(word)}`)
  if (!res.ok) return []
  const data = await res.json()
  return data.images || []
})

// fetch audio for a word
ipcMain.handle('get-audio', async (_, word) => {
  const res = await fetch(`${FLASK_URL}/audio/${encodeURIComponent(word)}`)
  if (!res.ok) return null
  return res.json()
})

// improve a translation via Claude
ipcMain.handle('improve-translation', async (_, word, definitionIndex) => {
  const res = await fetch(`${FLASK_URL}/improve-translation`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ word, definition_index: definitionIndex }),
  })
  if (!res.ok) return null
  return res.json()
})

// create an Anki card
ipcMain.handle('create-card', async (_, cardData) => {
  const res = await fetch(`${FLASK_URL}/create-card`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cardData),
  })
  return res.json()
})

// get available Anki decks
ipcMain.handle('get-decks', async () => {
  try {
    const res = await fetch(`${FLASK_URL}/decks`)
    if (!res.ok) return []
    const data = await res.json()
    return data.decks || []
  } catch {
    return []
  }
})

// play audio file natively via macOS afplay
ipcMain.on('play-audio', (_, filePath) => {
  const { exec } = require('child_process')
  const path = require('path')
  // resolve relative paths against the app's working directory
  const absolutePath = path.isAbsolute(filePath)
    ? filePath
    : path.resolve(app.getAppPath(), '..', filePath)
  exec(`afplay "${absolutePath}"`, (err) => {
    if (err) console.error('Audio playback error:', err)
  })
})

// hide the window after card creation
ipcMain.on('hide-window', () => {
  mainWindow?.hide()
})

// ---------------------------------------------------------------------------
// App lifecycle
// ---------------------------------------------------------------------------

app.whenReady().then(() => {
  createWindow()
  registerHotkey()
})

app.on('will-quit', () => {
  globalShortcut.unregisterAll()
})

// on Mac, keep app running even when all windows are closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
