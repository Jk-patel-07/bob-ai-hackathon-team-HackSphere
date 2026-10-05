import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],

  build: {
    // Output directly into the FastAPI static folder so one `uvicorn` process
    // serves both the API and the React SPA on the same port (8000).
    outDir: new URL('../backend/static', import.meta.url).pathname.replace(/^\/([A-Z]:)/, '$1'),
    emptyOutDir: true,
  },

  server: {
    port: 5173,
    proxy: {
      // During development the Vite dev server proxies API calls to FastAPI.
      // In production the built files are served by FastAPI itself — no proxy needed.
      '/health':     { target: 'http://localhost:8000', changeOrigin: true },
      '/search':     { target: 'http://localhost:8000', changeOrigin: true },
      '/ingest':     { target: 'http://localhost:8000', changeOrigin: true },
      '/categories': { target: 'http://localhost:8000', changeOrigin: true },
      '/documents':  { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
