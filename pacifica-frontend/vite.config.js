// vite.config.js (ฉบับสมบูรณ์)

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import basicSsl from '@vitejs/plugin-basic-ssl'
import path from 'path' // <-- 1. ตรวจสอบว่ามี import นี้

export default defineConfig({
  plugins: [
    react(),
    basicSsl()
  ],
  server: {
    port: 5173,
    https: true,
    host: '127.0.0.1',
  },
  // --- 2. ตรวจสอบให้แน่ใจว่ามีส่วนนี้อยู่ ---
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})