// src/App.jsx (ฉบับสมบูรณ์ที่เรียบง่ายและถูกต้องที่สุด)

import React from 'react';
import { Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

import { FiPlusSquare, FiUsers } from 'react-icons/fi';
import LoginPage from './pages/LoginPage.jsx';
import UserManagementPage from './pages/UserManagementPage.jsx';
import UserListPage from './pages/UserListPage.jsx';
import LogoutButton from './components/LogoutButton.jsx';
import ProtectedRoute from './components/ProtectedRoute.jsx';

import './App.css';

function App() {
    const { user, loading } = useAuth();
    const isSuperuser = user && user.is_superuser;

    if (loading) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <p>Loading Application...</p>
            </div>
        );
    }

    return (
        <div className="app-container">
            <header className="app-header">
                <h1 className="header-title">PACIFICA User Management System</h1>
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
                    <Route path="/login" element={<LoginPage />} />
                    
                    <Route element={<ProtectedRoute />}>
                        <Route path="/" element={<UserManagementPage isEditMode={false} />} />
                        <Route path="/user-list" element={<UserListPage />} />
                        <Route path="/user/:userId/edit" element={<UserManagementPage isEditMode={true} />} />
                    </Route>

                    <Route path="*" element={<Navigate to={user ? "/" : "/login"} replace />} />
                </Routes>
            </main>
        </div>
    );
}

export default App;