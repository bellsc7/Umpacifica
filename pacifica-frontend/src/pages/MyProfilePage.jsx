import React, { useState, useEffect } from 'react';
import axios from '../axiosConfig.js';

const MyProfilePage = () => {
  const [profile, setProfile] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      // *** หมายเหตุ: เราต้องตั้งค่าให้ Axios ส่ง token ไปกับ request ด้วย ***
      // *** ซึ่งปกติจะทำหลังจากสร้างระบบ Login/Logout ใน React แล้ว ***
      // *** แต่ตอนนี้เราจะใช้ session ที่ได้จากการ login ผ่าน Browsable API ไปก่อน ***
      try {
        const profileResponse = await axios.get('/api/my-profile/');
        const logsResponse = await axios.get('/api/my-logs/');
        
        setProfile(profileResponse.data);
        setLogs(logsResponse.data);
      } catch (error) {
        console.error("Error fetching data:", error);
        // อาจจะ redirect ไปหน้า login ถ้าเจอ error 401/403
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <p>Loading profile...</p>;
  }

  if (!profile) {
    return <p>Could not load profile data. Are you logged in?</p>;
  }

  return (
    <div>
      <h2>My Profile</h2>
      <p><strong>Name:</strong> {profile.full_name_eng}</p>
      <p><strong>Position:</strong> {profile.position}</p>

      <hr />

      <h3>My Current Permissions</h3>
      {profile.permissions && profile.permissions.length > 0 ? (
        <ul>
          {profile.permissions.map(perm => (
            <li key={perm.id}>{perm.system.name} - {perm.name}</li>
          ))}
        </ul>
      ) : (
        <p>No permissions assigned.</p>
      )}

      <hr />

      <h3>My Change History</h3>
      <table border="1" style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th style={{width: '25%'}}>Date</th>
            <th>Action</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log, index) => (
            <tr key={index}>
              <td>{new Date(log.timestamp).toLocaleString()}</td>
              <td>{log.action}</td>
              <td style={{ whiteSpace: 'pre-wrap' }}>{log.details}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MyProfilePage;