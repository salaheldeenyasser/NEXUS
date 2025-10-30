import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import T9PinKeypad from '../components/T9PinKeypad';
import axios from 'axios';
import classes from '../styles/selectProfile.module.css'

export default function ChangePINPage() {
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [showKeypad, setShowKeypad] = useState(true);
  const navigate = useNavigate();

  const handleConfirm = async (newPin) => {
    // Validate PIN length is at least 4 digits
    if (newPin.length !== 4) {
      setShowKeypad(false);
      setError('PIN must be 4 digits long');
      return;
    }
    
    try {
        await axios.post('http://localhost:8000/admin/change-pin', null, {
            params: { new_pin: newPin },
          });
      setSuccess(true);
      setError('');
      setShowKeypad(false);
    } catch (err) {
      setShowKeypad(false);
      setError(err.response?.data?.detail || 'Failed to change PIN');
    }
  };

  const handleCancel = () => {
    setShowKeypad(false);
  };

  const goBack = () => {
    navigate('/settings/system-settings');
  }

  return (
    <div>
      <h2 style={{ marginLeft: '10px' }}>Change Device PIN</h2>
      {showKeypad ? (
        <>
          <T9PinKeypad onConfirm={handleConfirm} onCancel={handleCancel} />
          {error && <p style={{ color: 'red', textAlign: 'center', marginTop: '10px' }}>{error}</p>}
        </>
      ) : success ? (
        <div>
            <p style={{ color: 'green', marginLeft: '25px', textAlign: 'center' }}>PIN changed successfully!</p>
            <h3 className={classes.back} onClick={goBack}>Back</h3>
        </div>
      ) : (
        <div>
            <p style={{ color: 'gray', marginLeft: '25px' }}>{error}</p>
            <h3 className={classes.back} onClick={goBack}>Back</h3>
        </div>
      )}
    </div>
  );
}