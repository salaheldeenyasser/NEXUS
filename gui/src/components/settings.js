import classes from '../styles/settings.module.css';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';

export default function Settings() {
  const navigate = useNavigate();
  const [securityLevel, setSecurityLevel] = useState(1);

  // Fetch min_required from backend
  useEffect(() => {
    fetch('http://localhost:8000/settings/system-settings')
      .then(res => res.json())
      .then(data => {
        if (data.min_required !== undefined) {
          setSecurityLevel(data.min_required);
        }
      })
      .catch(err => {
        console.error('Failed to fetch system settings:', err);
      });
  }, []);

  const handleLevelChange = async (e) => {
    const level = parseInt(e.target.value);
    setSecurityLevel(level);

    try {
      await fetch('http://localhost:8000/settings/system-settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ min_required: level }),
      });
    } catch (err) {
      console.error('Failed to update security level:', err);
    }
  };

  const goHome = () => navigate('/');
  const goProfCho = () => navigate('/settings/profile-choice-menu');
  const goSysSettings = () => navigate('/settings/system-settings');

  return (
    <div>
      <ul className={classes.ulSettings}>
        <li className={classes.liSettings} onClick={goProfCho}>User Management</li>

        <li className={classes.liSettings}>
          <label className={classes.dropdownLabel}>
            Required Security Methods:
            <select
              className={classes.dropdown}
              value={securityLevel}
              onChange={handleLevelChange}
            >
              <option value={1}>1</option>
              <option value={2}>2</option>
              <option value={3}>3</option>
            </select>
          </label>
        </li>

        <li className={classes.liSettings} onClick={goSysSettings}>System Settings</li>
      </ul>

      <h3 className={classes.back} onClick={goHome}>Back</h3>
    </div>
  );
}
