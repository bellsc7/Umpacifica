// src/pages/UserListPage.jsx (ฉบับสมบูรณ์)

import React, { useState, useEffect } from 'react';
import axios from '../axiosConfig';
import { Link } from 'react-router-dom';

const UserListPage = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);

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
                fetchUsers(); // Refresh the list
            } catch (error) {
                alert('Failed to delete user.');
                console.error("Error deleting user:", error);
            }
        }
    };

    if (loading) {
        return <p>Loading users...</p>;
    }

    return (
        <div>
            <h2>All Users</h2>
            <table border="1" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                    <tr>
                        <th>Employee ID</th>
                        <th>Username</th>
                        <th>Full Name (Eng)</th>
                        <th>Department</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {users.map(user => (
                        <tr key={user.id}>
                            <td>{user.employee_id || 'N/A'}</td>
                            <td>{user.username}</td>
                            <td>{user.full_name_eng}</td>
                            <td>{user.department}</td>
                            <td>
                                <Link to={`/user/${user.id}/edit`} style={{ marginRight: '10px' }}>Edit</Link>
                                <button onClick={() => handleDelete(user.id, user.username)}>Delete</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default UserListPage;