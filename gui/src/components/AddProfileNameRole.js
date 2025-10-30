import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import classes from '../styles/addProfileNameRole.module.css';
import T9NameKeypad from './T9NameKeypad';

export default function AddProfileNameRole() {
  const [name, setName] = useState('');
  const [role, setRole] = useState('user');
  const [showNameKeypad, setShowNameKeypad] = useState(false);
  const navigate = useNavigate();

  const handleNext = async () => {
    if (name.trim() === '') return;

    try {
      const response = await fetch('http://localhost:8000/gui/create_basic_user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: name.trim(), role })
      });

      const result = await response.json();

      if (result.success) {
        navigate('/settings/profile-choice-menu/add-profile/fingerprint', {
          state: { id: result.user_id, name: name.trim(), role }
        });
      } else {
        console.error('Failed to create user:', result.error);
      }
    } catch (err) {
      console.error('Error creating user:', err);
    }
  };

  const goBack = () => {
    navigate('/settings/profile-choice-menu');
  };

  return (
    <div className={classes.container}>
      <h2 className={classes.heading}>Enter Profile Info</h2>

      <label className={classes.label}>Name:</label>
      <div className={classes.input} onClick={() => setShowNameKeypad(true)} style={{ cursor: 'pointer' }}>
        {name || 'Tap to enter name'}
      </div>

      <label className={classes.label}>Role:</label>
      <ul className={classes.ulSettings} style={{ marginTop: '10px' }}>
        <li className={classes.liSettings} onClick={() => setRole('user')} style={role === 'user' ? { backgroundColor: 'gray' } : {}}>User</li>
        <li className={classes.liSettings} onClick={() => setRole('admin')} style={role === 'admin' ? { backgroundColor: 'gray' } : {}}>Admin</li>
      </ul>

      <h3 className={classes.nextBtn} onClick={handleNext}>Next</h3>
      <h3 className={classes.back} onClick={goBack}>Back</h3>

      {showNameKeypad && (
        <T9NameKeypad
          onConfirm={(value) => {
            setName(value);
            setShowNameKeypad(false);
          }}
          onCancel={() => setShowNameKeypad(false)}
        />
      )}
    </div>
  );
}
