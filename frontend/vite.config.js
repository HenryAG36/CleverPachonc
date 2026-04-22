import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Forward /api/* to the local Flask server during development
      '/api': 'http://localhost:5000',
    },
  },
})
