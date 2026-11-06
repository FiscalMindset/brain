import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev server proxies /api → the SecondBrain backend (apps/api).
// Production builds use same-origin /api; configure a reverse proxy there.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: 4173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
