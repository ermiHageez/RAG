import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/copilot': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/mcp': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/rag': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/memory': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/marketing': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/sales': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/agent': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
    },
  },
})
