import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        // Semantic vendor chunks: they change far less often than app code,
        // so they stay cache-stable across app-only deploys. Membership is a
        // package-name match. There is deliberately NO catch-all bucket: a
        // forced vendor-misc chunk once carried speed-insights + lucide +
        // vue-sonner + cva together and produced a cross-chunk TDZ ordering
        // failure on Vercel's Linux build ("Cannot access 'q' before
        // initialization" → blank page). Rollup's default splitting keeps the
        // leftovers cycle-safe; only dependency-clean one-way groups stay here.
        manualChunks(id) {
          if (!id.includes('node_modules')) return undefined
          if (/[\\/]node_modules[\\/](marked|dompurify)[\\/]/.test(id)) return 'vendor-markdown'
          if (/[\\/]node_modules[\\/]reka-ui[\\/]/.test(id)) return 'vendor-reka'
          if (/[\\/]node_modules[\\/](@vueuse|@vue[\\/]|vue|vue-router)[\\/]/.test(id)) return 'vendor-vue'
          return undefined
        },
      },
    },
  },
})
