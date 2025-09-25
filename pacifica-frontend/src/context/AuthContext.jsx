// src/context/AuthContext.jsx (ฉบับสมบูรณ์)

import React, { createContext, useState, useContext, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from '@/axiosConfig.js';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate(); // <-- ใช้ useNavigate ที่นี่

    const fetchUser = useCallback(async () => {
        const token = localStorage.getItem('authToken');
        if (token) {
            axios.defaults.headers.common['Authorization'] = `Token ${token}`;
            try {
                const response = await axios.get('/api/me/');
                setUser(response.data);
            } catch {
                localStorage.removeItem('authToken');
                delete axios.defaults.headers.common['Authorization'];
                setUser(null);
            }
        }
        setLoading(false);
    }, []);

    useEffect(() => {
        fetchUser();
    }, [fetchUser]);

    const login = async (username, password) => {
        try {
            const response = await axios.post('/api/login/', { username, password });
            const { token } = response.data;
            localStorage.setItem('authToken', token);
            axios.defaults.headers.common['Authorization'] = `Token ${token}`;
            await fetchUser();
            navigate('/'); // <-- **ทำการ Redirect ที่นี่!**
        } catch (error) {
            console.error("Login failed:", error);
            throw error; // ส่ง error กลับไปให้ LoginPage แสดงผล
        }
    };

    const logout = () => {
        try {
            axios.post('/api/logout/');
        } catch (error) {
            console.error("Logout request failed:", error);
        } finally {
            localStorage.removeItem('authToken');
            delete axios.defaults.headers.common['Authorization'];
            setUser(null);
            navigate('/login');
        }
    };

    const value = { user, login, logout, loading, isAuthenticated: !!user };

    return (
        <AuthContext.Provider value={value}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    return useContext(AuthContext);
};