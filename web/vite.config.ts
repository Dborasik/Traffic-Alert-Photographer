import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const backendPort = process.env.PORT ?? '5000'
const backend = `http://localhost:${backendPort}`

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': backend,
      '/incidents': backend,
    },
  },
})
