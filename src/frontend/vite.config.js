
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Vite config for React dashboard. Sets up plugins, proxy for API, output dir, and manual chunking for vendor/code splitting.
// Why: Enables fast dev server, optimized builds, and API proxying for local development.
// Root Cause: Missing or misconfigured Vite config breaks builds and slows dev workflow.
// Context: Used by all frontend devs and CI. Future: add env var support and more chunking.
// Model Suitability: Vite config logic is standard; GPT-4.1 is sufficient.
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/v1': 'http://localhost:8000'
    }
  },
  build: {
    outDir: '../static',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          charts: ['recharts'],
          icons: ['lucide-react']
        }
      }
    }
  }
})
