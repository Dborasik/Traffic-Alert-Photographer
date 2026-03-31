import path from 'path'
import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  // Read PORT from the project root .env (same file Flask uses)
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '')
  const backend = `http://localhost:${env.PORT ?? '5000'}`

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/api': backend,
        '/incidents': backend,
      },
    },
  }
})
