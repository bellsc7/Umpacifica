// src/components/Layout.jsx
import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import LogoutButton from './LogoutButton.jsx';
import { FiPlusSquare, FiUsers } from 'react-icons/fi';

const Layout = () => {
    const { user } = useAuth();
    const isSuperuser = user && user.is_superuser;

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
                <Outlet /> {/* <-- หน้าต่างๆ (Create, List, Edit) จะถูกแสดงที่นี่ */}
            </main>
        </div>
    );
};

export default Layout;