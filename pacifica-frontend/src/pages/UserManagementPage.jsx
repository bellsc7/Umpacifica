// src/pages/UserManagementPage.jsx (ฉบับสมบูรณ์)

import React, { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from '../axiosConfig';
import './UserManagementPage.css';

const UserManagementPage = ({ isEditMode = false }) => {
    const { userId } = useParams();
    const navigate = useNavigate();

    // --- State Management ---
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        email: '',
        first_name: '',
        last_name: '',
        employee_id: '',
        full_name_eng: '',
        full_name_thai: '',
        position: '',
        phone: '',
        company: '',
        department: '',
        brand: '',
        user_status: 'Current',
        has_pacifica_app: false,
        has_color_printing: false,
        has_cctv: false,
        has_vpn: false,
        has_wifi_other_devices: false,
        software_request: '',
        share_drive_request: '',
    });

    const [allPermissions, setAllPermissions] = useState([]);
    const [selectedPermissions, setSelectedPermissions] = useState(new Set());
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [generatedUsername, setGeneratedUsername] = useState('');

    // --- Data Fetching ---
    useEffect(() => {
        const fetchInitialData = async () => {
            setLoading(true);
            setError('');
            try {
                // ดึงข้อมูล Permissions เสมอ
                const permissionsResponse = await axios.get('/api/permissions/');
                setAllPermissions(permissionsResponse.data);

                // ถ้าเป็นโหมดแก้ไข ให้ดึงข้อมูล User มาด้วย
                if (isEditMode && userId) {
                    const userResponse = await axios.get(`/api/users/${userId}/`);
                    const userData = userResponse.data;
                    
                    // นำข้อมูลที่ได้มาใส่ในฟอร์ม
                    setFormData({
                        username: userData.username || '',
                        password: '', // ไม่ดึง password มาแสดง
                        email: userData.email || '',
                        first_name: userData.first_name || '',
                        last_name: userData.last_name || '',
                        employee_id: userData.employee_id || '',
                        full_name_eng: userData.full_name_eng || '',
                        full_name_thai: userData.full_name_thai || '',
                        position: userData.position || '',
                        phone: userData.phone || '',
                        company: userData.company || '',
                        department: userData.department || '',
                        brand: userData.brand || '',
                        user_status: userData.user_status || 'Current',
                        has_pacifica_app: userData.has_pacifica_app || false,
                        has_color_printing: userData.has_color_printing || false,
                        has_cctv: userData.has_cctv || false,
                        has_vpn: userData.has_vpn || false,
                        has_wifi_other_devices: userData.has_wifi_other_devices || false,
                        software_request: userData.software_request || '',
                        share_drive_request: userData.share_drive_request || '',
                    });
                    
                    // นำ permissions ที่ user คนนี้มีอยู่แล้วมาใส่ใน state
                    const userPermissionIds = new Set(userData.permissions.map(p => p.id));
                    setSelectedPermissions(userPermissionIds);
                }
            } catch (err) {
                setError('Could not load data. Please try again later.');
                console.error("Failed to fetch data:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchInitialData();
    }, [isEditMode, userId]);

    // --- Data Processing ---
    const groupedPermissions = useMemo(() => {
        return allPermissions.reduce((acc, permission) => {
            const systemName = permission.system.name;
            if (!acc[systemName]) { acc[systemName] = []; }
            acc[systemName].push(permission);
            return acc;
        }, {});
    }, [allPermissions]);

    // --- Handler Functions ---
    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        const newFormData = { ...formData, [name]: type === 'checkbox' ? checked : value };
        setFormData(newFormData);
        
        if (name === 'full_name_eng' && !isEditMode) {
            const nameParts = value.trim().split(/\s+/);
            if (nameParts.length > 0 && nameParts[0]) {
                const firstName = nameParts[0].toLowerCase();
                const lastNamePart = nameParts.length > 1 && nameParts[nameParts.length - 1] 
                    ? nameParts[nameParts.length - 1].substring(0, 2).toLowerCase() : '';
                setGeneratedUsername(`${firstName}${lastNamePart ? '_' + lastNamePart : ''}`);
            } else { setGeneratedUsername(''); }
        }
    };
    
    const handlePermissionChange = (permissionId) => {
        setSelectedPermissions(prev => {
            const newSelected = new Set(prev);
            if (newSelected.has(permissionId)) { newSelected.delete(permissionId); } 
            else { newSelected.add(permissionId); }
            return newSelected;
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        
        const submissionData = { ...formData, permission_ids: Array.from(selectedPermissions) };
        
        if (isEditMode) {
            // โหมดแก้ไข: ไม่ส่ง password ถ้าไม่ได้กรอก
            if (!submissionData.password) {
                delete submissionData.password;
            }
            try {
                await axios.patch(`/api/users/${userId}/`, submissionData);
                alert('User updated successfully!');
                navigate('/user-list');
            } catch (err) {
                // ... การจัดการ Error ...
            }
        } else {
            // โหมดสร้าง: ใช้ username และ password ที่สร้างขึ้น
            if (!formData.full_name_eng || !generatedUsername) {
                alert('Full Name (Eng) is required to generate a username.');
                return;
            }
            submissionData.username = generatedUsername;
            submissionData.password = 'Pec@2025#';
            try {
                await axios.post('/api/users/', submissionData);
                alert(`User '${generatedUsername}' created successfully!`);
                navigate('/user-list');
            } catch (err) {
                const errorData = err.response?.data;
                let errorMessage = 'Failed to create user.';
                if (errorData) {
                    errorMessage += `\n${Object.keys(errorData).map(key => `${key}: ${errorData[key]}`).join('\n')}`;
                }
                setError(errorMessage);
                alert(errorMessage);
                console.error('Error creating user:', errorData || err.message);
            }
        }
    };
    
    if (loading) return <div className="form-container"><p>Loading...</p></div>;

    return (
        <div className="form-container">
            <form onSubmit={handleSubmit}>
                <h1>{isEditMode ? `Edit User: ${formData.full_name_eng}` : 'Create New User'}</h1>
                {error && <div className="error-message">{error}</div>}

                <fieldset className="form-section">
                    <legend>Login Credentials</legend>
                    <div className="grid-container" style={{gridTemplateColumns: '1fr 1fr'}}>
                        <div className="form-group">
                            <label htmlFor="username">Username*</label>
                            {isEditMode ? (
                                <input type="text" id="username" name="username" value={formData.username} onChange={handleChange} required />
                            ) : (
                                <input type="text" value={generatedUsername} readOnly disabled style={{ backgroundColor: '#e9ecef' }} />
                            )}
                        </div>
                        <div className="form-group">
                            <label htmlFor="password">{isEditMode ? 'New Password (leave blank to keep current)' : 'Default Password'}</label>
                             {isEditMode ? (
                                <input type="password" id="password" name="password" value={formData.password} onChange={handleChange} />
                             ) : (
                                <input type="text" value="Pec@2025#" readOnly disabled style={{ backgroundColor: '#e9ecef' }} />
                             )}
                        </div>
                    </div>
                </fieldset>

                {/* --- ส่วนที่ 2: Employee Details (เพิ่มฟิลด์ให้ครบ) --- */}
                <fieldset className="form-section">
                    <legend>Employee Details</legend>
                    <div className="grid-container" style={{gridTemplateColumns: '1fr 1fr'}}>
                        <div className="form-group">
                            <label htmlFor="employee_id">Employee ID</label>
                            <input type="text" id="employee_id" name="employee_id" value={formData.employee_id} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label htmlFor="company">Company</label>
                            <input type="text" id="company" name="company" value={formData.company} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label htmlFor="full_name_eng">Full Name (Eng)*</label>
                            <input type="text" id="full_name_eng" name="full_name_eng" value={formData.full_name_eng} onChange={handleChange} required />
                        </div>
                        <div className="form-group">
                            <label htmlFor="department">Department</label>
                            <input type="text" id="department" name="department" value={formData.department} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label htmlFor="full_name_thai">Full Name (Thai)</label>
                            <input type="text" id="full_name_thai" name="full_name_thai" value={formData.full_name_thai} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label htmlFor="brand">Brand</label>
                            <input type="text" id="brand" name="brand" value={formData.brand} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label htmlFor="position">Position</label>
                            <input type="text" id="position" name="position" value={formData.position} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label htmlFor="phone">Phone</label>
                            <input type="text" id="phone" name="phone" value={formData.phone} onChange={handleChange} />
                        </div>
                        <div className="form-group">
                            <label htmlFor="email">Email</label>
                            <input type="email" id="email" name="email" value={formData.email} onChange={handleChange} />
                        </div>
                    </div>
                </fieldset>
                
                {/* --- ส่วนที่ 3: System/Services (เพิ่มกลับเข้ามา) --- */}
                <fieldset className="form-section">
                    <legend>Select System/Services</legend>
                    <div className="permission-grid">
                        <div className="checkbox-group">
                            <input type="checkbox" id="has_pacifica_app" name="has_pacifica_app" checked={formData.has_pacifica_app} onChange={handleChange} />
                            <label htmlFor="has_pacifica_app">Pacifica App</label>
                        </div>
                        <div className="checkbox-group">
                            <input type="checkbox" id="has_color_printing" name="has_color_printing" checked={formData.has_color_printing} onChange={handleChange} />
                            <label htmlFor="has_color_printing">Color Printing</label>
                        </div>
                        <div className="checkbox-group">
                            <input type="checkbox" id="has_cctv" name="has_cctv" checked={formData.has_cctv} onChange={handleChange} />
                            <label htmlFor="has_cctv">CCTV</label>
                        </div>
                        <div className="checkbox-group">
                            <input type="checkbox" id="has_vpn" name="has_vpn" checked={formData.has_vpn} onChange={handleChange} />
                            <label htmlFor="has_vpn">VPN</label>
                        </div>
                        <div className="checkbox-group">
                            <input type="checkbox" id="has_wifi_other_devices" name="has_wifi_other_devices" checked={formData.has_wifi_other_devices} onChange={handleChange} />
                            <label htmlFor="has_wifi_other_devices">Wifi for other devices</label>
                        </div>
                    </div>
                    <div className="grid-container" style={{ marginTop: '1.5rem', gridTemplateColumns: '1fr 1fr' }}>
                        <div className="form-group">
                            <label htmlFor="software_request">Software (Please Specify)</label>
                            <input type="text" id="software_request" name="software_request" value={formData.software_request} onChange={handleChange} placeholder="e.g., Adobe Photoshop" />
                        </div>
                        <div className="form-group">
                            <label htmlFor="share_drive_request">Share Drive (Please Specify)</label>
                            <input type="text" id="share_drive_request" name="share_drive_request" value={formData.share_drive_request} onChange={handleChange} placeholder="e.g., //server/marketing" />
                        </div>
                    </div>
                </fieldset>

                <fieldset className="form-section">
                    <legend>Permission Level</legend>
                    {allPermissions.length > 0 ? (
                        <div className="permission-grid">
                            {Object.entries(groupedPermissions).map(([systemName, permissions]) => (
                                <div key={systemName} className="permission-group">
                                    <h4>{systemName}</h4>
                                    {permissions.map(permission => (
                                        <div key={permission.id} className="checkbox-group">
                                            <input
                                                type="checkbox"
                                                id={`perm-${permission.id}`}
                                                checked={selectedPermissions.has(permission.id)}
                                                onChange={() => handlePermissionChange(permission.id)}
                                            />
                                            <label htmlFor={`perm-${permission.id}`}>{permission.name}</label>
                                        </div>
                                    ))}
                                </div>
                            ))}
                        </div>
                    ) : ( <p>No permissions found.</p> )}
                </fieldset>

                <button type="submit" className="submit-button">
                    {isEditMode ? 'Save Changes' : 'Create User'}
                </button>
            </form>
        </div>
    );
};

export default UserManagementPage;