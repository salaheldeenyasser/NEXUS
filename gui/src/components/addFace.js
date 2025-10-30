import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import classes from '../styles/addFace.module.css';

const AddFace = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { id, name, role, fingerprint_position, cameFrom } = location.state || {};
  const isEditing = Boolean(id && cameFrom === 'editProfile');

  const [isCapturing, setIsCapturing] = useState(false);
  const [message, setMessage] = useState('Look at the camera and press Capture.');

  useEffect(() => {
    const interval = setInterval(() => {
      fetch('http://localhost:8000/access/recent-logs')
        .then(res => res.json())
        .then(data => {
          if (data.length > 0) {
            setMessage(data[data.length - 1]);
          }
        })
        .catch(err => console.error('Failed to fetch logs', err));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const captureFace = async () => {
    setIsCapturing(true);
    setMessage('Capturing face...');

    try {
      const endpoint = isEditing
        ? 'http://localhost:8000/gui/retake_face_embeddings'
        : 'http://localhost:8000/gui/add_face';

      const body = JSON.stringify({ user_id: id });

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
      });

      const result = await response.json();

      if (result.success) {
        setMessage(isEditing ? 'Face updated successfully!' : 'Face captured!');
        setTimeout(() => {
          if (isEditing) {
            navigate('/settings/profile-choice-menu/manage-profiles');
          } else {
            navigate('/');
          }
        }, 3000);
      } else {
        setMessage(`Failed: ${result.error || 'Unknown error'}`);
      }
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setIsCapturing(false);
    }
  };

  const goBack = () => {
    navigate('/settings/profile-choice-menu/add-profile/fingerprint', {
      state: { name, role, fingerprint_position },
    });
  };

  return (
    <div className={classes.container}>
      <h2 className={classes.heading}>Face Enrollment</h2>
      <p className={classes.message}>{message}</p>

      <div className={classes.cameraPreview}>
        <div className={classes.placeholderBox}>
          <div className={classes.cameraFrame}></div>
        </div>
      </div>

      <button className={classes.button} onClick={captureFace} disabled={isCapturing}>
        {isCapturing ? 'Processing...' : isEditing ? 'Retake Face' : 'Capture Face'}
      </button>

      <h3 className={classes.back} onClick={goBack}>Back</h3>
    </div>
  );
};

export default AddFace;