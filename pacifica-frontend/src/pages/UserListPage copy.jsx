// src/pages/UserListPage.jsx (ฉบับที่ถูกต้อง)

import React, { useState, useEffect, useMemo } from 'react';
import axios from '../axiosConfig'; // หรือ '@/axiosConfig'
import { Link } from 'react-router-dom';
import { FiEdit, FiTrash2, FiSearch, FiPlus, FiSlash, FiCheckCircle } from 'react-icons/fi'; // <-- เพิ่ม icon
import './UserListPage.css';

const UserListPage = () => {
    const [allUsers, setAllUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const response = await axios.get('/api/users/');
            setAllUsers(response.data);
        } catch (error) {
            console.error("Error fetching users:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleRevoke = async (userId, username) => {
        if (window.confirm(`Are you sure you want to REVOKE access for user: ${username}?`)) {
            try {
                await axios.post(`/api/users/${userId}/revoke/`);
                alert('User revoked successfully!');
                fetchUsers();
            } catch (error) {
                alert('Failed to delete user.');
                console.error("Error deleting user:", error);
            }
        }
    };

    const { activeUsers, revokedUsers } = useMemo(() => {
        const filtered = allUsers.filter(user =>
            (user.username?.toLowerCase().includes(searchTerm.toLowerCase())) ||
            (user.full_name_eng?.toLowerCase().includes(searchTerm.toLowerCase()))
        );
        
        // แยก User ออกเป็น 2 กลุ่มตาม is_active
        return {
            activeUsers: filtered.filter(user => user.is_active),
            revokedUsers: filtered.filter(user => !user.is_active),
        };
    }, [allUsers, searchTerm]);

    const UserTable = ({ users, isRevokedTable = false }) => (
        <div className="table-container">
            <table className="data-table">
                <thead>
                    <tr>
                        <th>Employee ID</th>
                        <th>Username</th>
                        <th>Full Name (Eng)</th>
                        <th>Department</th>
                        <th style={{ textAlign: 'center' }}>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {users.length > 0 ? (
                        users.map(user => (
                            <tr key={user.id}>
                                <td>{user.employee_id || 'N/A'}</td>
                                <td>{user.username}</td>
                                <td>{user.full_name_eng}</td>
                                <td>{user.department}</td>
                                <td className="action-buttons">
                                    <Link to={`/user/${user.id}/edit`} className="button button-edit">
                                        <FiEdit /> Edit
                                    </Link>
                                    {/* แสดงปุ่ม Revoke สำหรับ Active Users */}
                                    {!isRevokedTable && (
                                         <button onClick={() => handleRevoke(user.id, user.username)} className="button button-revoke">
                                            <FiSlash /> Revoke
                                        </button>
                                    )}
                                    {/* (ทางเลือก) อาจจะเพิ่มปุ่ม "Re-activate" สำหรับ Revoked Users */}
                                </td>
                            </tr>
                        ))
                    ) : (
                        <tr><td colSpan="5" style={{ textAlign: 'center', padding: '2rem' }}>No users found.</td></tr>
                    )}
                </tbody>
            </table>
        </div>
    );

    if (loading) {
        return <p>Loading users...</p>;
    }

    return (
        <div className="user-list-container">
            <div className="list-header">
                <h2>User Management</h2>
                {/* Search and Create button เหมือนเดิม */}
            </div>

            {/* --- ตารางสำหรับ Active Users --- */}
            <div className="table-section">
                <h3 className="table-title"><FiCheckCircle /> Active Users ({activeUsers.length})</h3>
                <UserTable users={activeUsers} />
            </div>

            {/* --- ตารางสำหรับ Revoked Users --- */}
            <div className="table-section">
                <h3 className="table-title"><FiSlash /> Revoked Users ({revokedUsers.length})</h3>
                <UserTable users={revokedUsers} isRevokedTable={true} />
            </div>
        </div>
    );
};

export default UserListPage;