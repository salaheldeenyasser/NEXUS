import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import classes from '../styles/createAdmin.module.css';
import T9NameKeypad from './T9NameKeypad';
import T9PinKeypad from './T9PinKeypad';

export default function CreateAdmin() {
  const [name, setName] = useState('');
  const [pin, setPin] = useState('');
  const [pinConfirmed, setPinConfirmed] = useState(false);
  const [showNameKeypad, setShowNameKeypad] = useState(false);
  const [showPinKeypad, setShowPinKeypad] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async () => {
    if (!name.trim() || !pin.trim()) return;
    if (pin.length !== 4 || !/^\d{4}$/.test(pin)) {
      setError('PIN must be 4 digits');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Step 1: Create the admin user with face pipeline only
      const addUserRes = await fetch('http://localhost:8000/gui/add_user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(),
          role: 'admin',
          apply_finger_pipeline: false,
          apply_face_pipeline: true
        })
      });

      const userData = await addUserRes.json();
      if (!userData.success) {
        throw new Error(userData.error || 'Failed to create admin user');
      }

      const user_id = userData.user_id;

      // Step 2: Set the admin PIN
      const changePinRes = await fetch(
        `http://localhost:8000/admin/change-admin-pin?new_pin=${pin}`,
        { method: 'POST' }
      );

      const pinResult = await changePinRes.json();
      if (pinResult.status !== 'success') {
        throw new Error(pinResult.message || 'Failed to update admin PIN');
      }

      // Step 3: Go directly to face enrollment screen
      navigate('/settings/profile-choice-menu/add-profile/face', {
        state: {
          id: user_id,
          name: name.trim(),
          role: 'admin',
          cameFrom: 'createAdmin'
        }
      });

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className={classes.container}>
      <h2 className={classes.heading}>Initial Admin Setup</h2>

      {error && <p className={classes.error}>{error}</p>}

      <label className={classes.label}>Name:</label>
      <div
        className={classes.input}
        onClick={() => setShowNameKeypad(true)}
        style={{ cursor: 'pointer' }}
      >
        {name || 'Tap to enter name'}
      </div>

      <label className={classes.label}>PIN:</label>
      <div
        className={classes.input}
        onClick={() => {
          setShowPinKeypad(true);
          setPinConfirmed(false);
        }}
        style={{ cursor: 'pointer' }}
      >
        {pin
          ? pinConfirmed
            ? '•'.repeat(pin.length)
            : pin
          : 'Tap to enter PIN'}
      </div>

      <button
        className={classes.button}
        onClick={handleSubmit}
        disabled={!name || !pin || loading}
      >
        {loading ? 'Processing...' : 'Continue'}
      </button>

      {showNameKeypad && (
        <T9NameKeypad
          onConfirm={(value) => {
            setName(value);
            setShowNameKeypad(false);
          }}
          onCancel={() => setShowNameKeypad(false)}
        />
      )}

      {showPinKeypad && (
        <T9PinKeypad
          onConfirm={(value) => {
            setPin(value);
            setPinConfirmed(true);
            setShowPinKeypad(false);
          }}
          onCancel={() => setShowPinKeypad(false)}
        />
      )}
    </div>
  );
}
