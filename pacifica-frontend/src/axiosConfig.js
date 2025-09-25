// src/axiosConfig.js (ฉบับแก้ไข)

import axios from 'axios';

// --- เพิ่มบรรทัดนี้เข้าไป ---
//axios.defaults.baseURL = 'https://127.0.0.1:8000'; // ใช้ HTTPS

// ตั้งค่าให้ Axios ส่ง Cookies ไปกับทุก request ที่เป็น cross-origin
axios.defaults.withCredentials = true;

// ตั้งค่าให้ Axios อ่าน CSRF token จาก cookie ที่ชื่อ 'csrftoken'
// แล้วส่งไปใน Header ที่ชื่อ 'X-CSRFToken'
axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

console.log('AXIOS INSTANCE HAS BEEN CONFIGURED!');

axios.interceptors.request.use(config => {
    // ดึง token จาก localStorage
    const token = localStorage.getItem('authToken');
    if (token) {
        // ถ้ามี token, ให้เพิ่ม Authorization header
        config.headers['Authorization'] = `Token ${token}`;
    }
    return config;
});


export default axios;