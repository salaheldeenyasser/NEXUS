import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import T9PinKeypad from '../components/T9PinKeypad';
import axios from 'axios';
import classes from '../styles/selectProfile.module.css';

export default function ChangeAdminPINPage() {
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [showKeypad, setShowKeypad] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();
  const profileId = location.state?.id;

  const handleConfirm = async (newPin) => {
    // Validate PIN length is at least 4 digits
    if (newPin.length !== 4) {
      setShowKeypad(false);
      setError('PIN must be 4 digits long');
      return;
    }
    
    try {
        // Make sure the API endpoint matches your FastAPI route
        await axios.post('http://localhost:8000/admin/change-admin-pin', null, {
            params: { new_pin: newPin },
          });
      setSuccess(true);
      setError('');
      setShowKeypad(false);
    } catch (err) {
      setShowKeypad(false);
      setError(err.response?.data?.detail || 'Failed to change Admin PIN');
    }
  };

  const handleCancel = () => {
    setShowKeypad(false);
  };

  const goBack = () => {
    navigate(`/settings/profile-choice-menu/manage-profiles/edit-profile/${profileId}`);
  }

  return (
    <div>
      <h2 style={{ textAlign: 'center', marginTop: '20px' }}>Change Admin PIN</h2>
      {showKeypad ? (
        <>
          <T9PinKeypad onConfirm={handleConfirm} onCancel={handleCancel} />
          {error && <p style={{ color: 'red', textAlign: 'center', marginTop: '10px' }}>{error}</p>}
        </>
      ) : success ? (
        <div>
            <p style={{ color: 'green', textAlign: 'center' }}>Admin PIN changed successfully!</p>
            <h3 className={classes.back} onClick={goBack}>Back</h3>
        </div>
      ) : (
        <div>
            <p style={{ color: 'gray', textAlign: 'center' }}>{error}</p>
            <h3 className={classes.back} onClick={goBack}>Back</h3>
        </div>
      )}
    </div>
  );
}