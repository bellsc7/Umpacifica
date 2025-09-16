import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import basicSsl from '@vitejs/plugin-basic-ssl' // <-- 1. Import plugin

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    basicSsl() // <-- 2. เพิ่ม plugin เข้าไป
  ],
  server: {
    // --- 3. เพิ่มส่วนนี้เข้าไป ---
    // เปลี่ยน Port และเปิด HTTPS
    port: 5173, // หรือ Port อื่นที่คุณต้องการ
    https: true,
    host: '127.0.0.1', // ระบุ host ให้ชัดเจน
  }
})