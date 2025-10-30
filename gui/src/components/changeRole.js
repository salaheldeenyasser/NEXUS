import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import classes from '../styles/systemSettings.module.css'

const ChangeRole = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [newRole, setNewRole] = useState('');
  const [currentProfile, setCurrentProfile] = useState(null);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch('http://localhost:8000/users/profiles/');
        const data = await response.json();
        const user = data.find((p) => p.id === id);

        if (!user) {
          setMessage('Profile not found.');
          return;
        }

        setCurrentProfile(user);
        setNewRole(user.role || 'user');
      } catch (error) {
        setMessage('Failed to fetch profile.');
      }
    };

    fetchProfile();
  }, [id]);

  const updateRole = async (role) => {
  try {
    const response = await fetch(`http://localhost:8000/users/update/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ role: role.toLowerCase() }),
    });

    const result = await response.json();

    if (!response.ok) {
      setMessage(result.detail || 'Failed to update role.');
      setTimeout(() => {
        navigate(`/settings/profile-choice-menu/manage-profiles/edit-profile/${id}`);
      }, 1500);
      return;
    }

    setMessage('Role updated successfully!');
    setTimeout(() => {
      navigate(`/settings/profile-choice-menu/manage-profiles/edit-profile/${id}`);
    }, 1000);
  } catch (error) {
    setMessage('Something went wrong while updating the role.');
    setTimeout(() => {
      navigate(`/settings/profile-choice-menu/manage-profiles/edit-profile/${id}`);
    }, 1500);
  }
};




const goBack = () => {
  navigate(`/settings/profile-choice-menu/manage-profiles/edit-profile/${id}`);
}


console.debug('Current role:', newRole, currentProfile);

  return (
  <div>
    <h2 style={{ textAlign: 'center' }}>Change Role</h2>
    
    {message && <p style={{ textAlign: 'center', color: message.includes("successfully") ? "green" : "red" }}>{message}</p>}

    <ul>
      <li className={classes.liSysSettings} onClick={() => updateRole("user")}>User</li>
      <li className={classes.liSysSettings} onClick={() => updateRole("admin")}>Admin</li>
    </ul>



    <h3 className={classes.back} onClick={goBack}>Back</h3>
  </div>
);


};

export default ChangeRole;
