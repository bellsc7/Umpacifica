// src/App.jsx (ฉบับเต็ม)
import React from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext'; // <-- ใช้ useAuth

import { FiPlusSquare, FiUsers } from 'react-icons/fi';
import LoginPage from './pages/LoginPage.jsx';
import UserManagementPage from './pages/UserManagementPage.jsx';
import UserListPage from './pages/UserListPage.jsx';
import LogoutButton from './components/LogoutButton.jsx';
//import SuperAdminRoute from './components/SuperAdminRoute.jsx'; // <-- import ยาม

import './App.css';

function App() {
    const { user, loading } = useAuth();
    // สร้างตัวแปร isSuperuser แค่ครั้งเดียว
    const isSuperuser = user && user.is_superuser;
    console.log('[App.jsx] RENDERING - Loading:', loading, 'IsSuperuser:', isSuperuser); // <-- Log 5

    // แสดงหน้า Loading ขณะที่ AuthContext กำลังตรวจสอบ Token
    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <p>Loading Application...</p>
            </div>
        );
    }

    return (
        <BrowserRouter>
            <div className="app-container">
                <header className="app-header">
                    <h1 className="header-title">PACIFICA User Management System</h1>
                    
                    {/* --- เงื่อนไขการแสดงผลเมนู (ใช้ isSuperuser) --- */}
                    {isSuperuser && (
                        <nav className="header-nav">
                            <NavLink to="/" className="nav-link">
                                <FiPlusSquare /> Create New User
                            </NavLink>
                            <NavLink to="/user-list" className="nav-link">
                                <FiUsers /> View All Users
                            </NavLink>
                            <LogoutButton />
                        </nav>
                    )}
                </header>
                <main className="main-content">
                    <Routes>
                        {isSuperuser ? (
                            // --- Routes สำหรับ Super Admin ---
                            <>
                                {console.log('[App.jsx] Rendering SUPERUSER routes')} {/* <-- Log 6 */}
                                <Route path="/" element={<UserManagementPage isEditMode={false} />} />
                                <Route path="/user-list" element={<UserListPage />} />
                                <Route path="/user/:userId/edit" element={<UserManagementPage isEditMode={true} />} />
                                {/* ถ้าเข้า URL ที่ไม่รู้จัก ให้กลับไปหน้าหลัก */}
                                <Route path="*" element={<Navigate to="/" replace />} />
                            </>
                        ) : (
                            // --- Routes สำหรับผู้ที่ยังไม่ได้ Login หรือไม่มีสิทธิ์ ---
                            <>
                                {console.log('[App.jsx] Rendering GUEST routes')} {/* <-- Log 7 */}
                                <Route path="/login" element={<LoginPage />} />
                                {/* ถ้าพยายามจะเข้าหน้าอื่น ให้ Redirect กลับไปหน้า Login */}
                                <Route path="*" element={<Navigate to="/login" replace />} />
                            </>
                        )}
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    );
}

export default App;