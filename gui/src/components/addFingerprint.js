import { useLocation, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import classes from '../styles/addFingerprint.module.css';

export default function AddFingerprint() {
  const location = useLocation();
  const navigate = useNavigate();
  const { id, name, role, fingerprint_position, cameFrom } = location.state || {};
  const isEditing = Boolean(id && cameFrom === 'editProfile');
  const [message, setMessage] = useState(isEditing ? 'Press to retake fingerprint.' : 'Press to enroll fingerprint.');

  useEffect(() => {
    const interval = setInterval(() => {
      fetch('http://localhost:8000/access/recent-logs')
        .then(res => res.json())
        .then(data => {
          if (data.length > 0) {
            const latest = data[data.length - 1];
            setMessage(latest);
          }
        })
        .catch(err => console.error("Failed to fetch recent logs:", err));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const enrollFingerprint = async () => {
    try {
      setMessage(isEditing ? 'Retaking fingerprint...' : 'Enrolling fingerprint...');
      const response = await fetch('http://localhost:8000/gui/add_fingerprint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: id })
      });

      const result = await response.json();

      if (result.success) {
        setMessage('Fingerprint updated successfully.');
        setTimeout(() => {
          if (isEditing) {
            navigate('/settings/profile-choice-menu/manage-profiles');
          } else {
            navigate('/settings/profile-choice-menu/add-profile/face', {
              state: { id, name, role, fingerprint_position: result.fingerprint_position }
            });
          }
        }, 2000);
      } else {
      setTimeout(() => setMessage(`Fingerprint failed: ${result.error || 'Unknown error'}`), 2000);
      }
    } catch (err) {
      setTimeout(() => setMessage('Error: ' + err.message), 2000);
    }
  };

  const goBack = () => {
    if (cameFrom === 'createAdmin') {
      navigate('/create-admin');
    } else if (isEditing) {
      navigate(`/settings/profile-choice-menu/manage-profiles/edit-profile/${id}`);
    } else {
      navigate('/settings/profile-choice-menu/add-profile');
    }
  };

  return (
    <div className={classes.container}>
      <h2 className={classes.heading}>Fingerprint Enrollment</h2>
      <p className={classes.message}>{message}</p>
      <button className={classes.button} onClick={enrollFingerprint}>
        {isEditing ? 'Retake Fingerprint' : 'Enroll Fingerprint'}
      </button>
      <h3 className={classes.back} onClick={goBack}>Back</h3>
    </div>
  );
}