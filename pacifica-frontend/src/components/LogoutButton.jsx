import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // <-- ใช้ useAuth
import { FiLogOut } from 'react-icons/fi';

const LogoutButton = () => {
    const navigate = useNavigate();
    const { logout } = useAuth(); // <-- ดึงฟังก์ชัน logout มา

    return (
        <button onClick={() => logout(navigate)} className="logout-button">
            <FiLogOut /> Logout
        </button>
    );
};
export default LogoutButton;