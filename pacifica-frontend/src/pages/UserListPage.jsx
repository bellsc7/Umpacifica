// src/pages/UserListPage.jsx (ฉบับที่ถูกต้อง)

import React, { useState, useEffect, useMemo } from 'react';
import axios from '../axiosConfig'; // หรือ '@/axiosConfig'
import { Link } from 'react-router-dom';
import { FiEdit, FiTrash2, FiSearch, FiPlus } from 'react-icons/fi';
import './UserListPage.css';

const UserListPage = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const response = await axios.get('/api/users/');
            setUsers(response.data);
        } catch (error) {
            console.error("Error fetching users:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleDelete = async (userId, username) => {
        if (window.confirm(`Are you sure you want to delete user: ${username}?`)) {
            try {
                await axios.delete(`/api/users/${userId}/`);
                alert('User deleted successfully!');
                fetchUsers();
            } catch (error) {
                alert('Failed to delete user.');
                console.error("Error deleting user:", error);
            }
        }
    };

    const filteredUsers = useMemo(() => {
        if (!searchTerm) {
            return users;
        }
        return users.filter(user =>
            (user.username?.toLowerCase().includes(searchTerm.toLowerCase())) ||
            (user.full_name_eng?.toLowerCase().includes(searchTerm.toLowerCase())) ||
            (user.department?.toLowerCase().includes(searchTerm.toLowerCase()))
        );
    }, [users, searchTerm]);

    if (loading) {
        return <p>Loading users...</p>;
    }

    return (
        <div className="user-list-container">
            <div className="list-header">
                <h2>All Users</h2>
                <div className="search-and-actions">
                    <div className="search-box">
                        <FiSearch className="search-icon" />
                        <input
                            type="text"
                            placeholder="Search by username, name, etc..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <Link to="/" className="button button-primary">
                        <FiPlus /> Create New User
                    </Link>
                </div>
            </div>

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
                        {filteredUsers.length > 0 ? (
                            filteredUsers.map(user => (
                                <tr key={user.id}>
                                    <td>{user.employee_id || 'N/A'}</td>
                                    <td>{user.username}</td>
                                    <td>{user.full_name_eng}</td>
                                    <td>{user.department}</td>
                                    <td className="action-buttons">
                                        <Link to={`/user/${user.id}/edit`} className="button button-edit">
                                            <FiEdit /> Edit
                                        </Link>
                                        <button onClick={() => handleDelete(user.id, user.username)} className="button button-delete">
                                            <FiTrash2 /> Delete
                                        </button>
                                    </td>
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="5" style={{ textAlign: 'center', padding: '2rem' }}>No users found.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default UserListPage;