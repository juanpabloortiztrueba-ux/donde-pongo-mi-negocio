import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev: vite escucha en 127.0.0.1:VITE_PUERTO y reenvia /api al backend (API_PUERTO, por defecto 8501).
// Build: web/dist con rutas relativas (base './'), para servirlo desde el backend o desde cualquier carpeta.
const api = `http://127.0.0.1:${process.env.API_PUERTO ?? 8501}`
export default defineConfig({
  base: './',
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: Number(process.env.VITE_PUERTO ?? 5173),
    strictPort: true,
    proxy: { '/api': { target: api, changeOrigin: true } },
  },
  build: { outDir: 'dist', emptyOutDir: true, modulePreload: false, chunkSizeWarningLimit: 1500 },
})
