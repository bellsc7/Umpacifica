// src/pages/LoginPage.jsx (ฉบับเต็ม)
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext'; // <-- ใช้ useAuth
import './LoginPage.css';

const LoginPage = ({ setIsLoggedIn }) => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useAuth(); // <-- ดึงฟังก์ชัน login มา

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await login(username, password);
            //navigate('/');
        } catch (err) {
            setError('Unable to log in with provided credentials.');
        } finally {
            // ไม่ว่าจะสำเร็จหรือล้มเหลว ให้หยุด loading เสมอ
            setLoading(false);
        }
    };
    return (
        <div className="login-container">
            <div className="login-box">
                <h2>Welcome Back!</h2>
                <form onSubmit={handleSubmit} className="login-form">
                    {error && <p className="login-error">{error}</p>}
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            required
                            placeholder="Enter your username"
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                            placeholder="Enter your password"
                        />
                    </div>
                    <button type="submit" className="login-button" disabled={loading}>
                        {loading ? 'Logging in...' : 'Log In'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default LoginPage;