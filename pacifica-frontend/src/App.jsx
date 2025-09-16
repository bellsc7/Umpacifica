// src/App.jsx (ฉบับแก้ไข)

import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import axios from './axiosConfig.js';

import UserManagementPage from './pages/UserManagementPage';
import UserListPage from './pages/UserListPage';

import './App.css';

function App() {
    // ... useEffect เหมือนเดิม ...
    useEffect(() => {
        const fetchCsrfToken = async () => {
            try {
                await axios.get('/api/get-csrf-token/');
                console.log('CSRF Token has been set by App.jsx');
            } catch (error) {
                console.error('Failed to fetch CSRF token from App.jsx:', error);
            }
        };
        fetchCsrfToken();
    }, []);

    return (
        <BrowserRouter>
            <div>
                {/* ... header และ nav เหมือนเดิม ... */}
                <header>
                    <h1>User Management System</h1>
                    <nav>
                        <Link to="/" style={{ marginRight: '1rem' }}>Create New User</Link>
                        <Link to="/user-list">View All Users</Link>
                    </nav>
                </header>
                <hr />
                <main>
                    <Routes>
                        {/* --- แก้ไข Route นี้ --- */}
                        {/* Route สำหรับสร้าง User: ส่ง isEditMode={false} ไปอย่างชัดเจน */}
                        <Route path="/" element={<UserManagementPage isEditMode={false} />} />

                        {/* Route สำหรับแสดงรายชื่อ User (เหมือนเดิม) */}
                        <Route path="/user-list" element={<UserListPage />} />

                        {/* Route สำหรับหน้าแก้ไข User (เหมือนเดิม) */}
                        <Route path="/user/:userId/edit" element={<UserManagementPage isEditMode={true} />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    );
}

export default App;