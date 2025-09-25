// src/components/ProtectedRoute.jsx
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = () => {
    // ตรวจสอบว่ามี token อยู่ใน localStorage หรือไม่
    const { isAuthenticated } = useAuth();
    // ถ้ามี token (ล็อกอินแล้ว) ให้แสดงหน้าที่ต้องการ (Outlet)
    // ถ้าไม่มี token ให้ redirect ไปยังหน้า /login
   return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;