import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './',   // important for Electron — use relative paths in built files
  root: 'src',
  build: {
    outDir: '../dist',  // output to electron/dist
  },
})