import React, { useState, useEffect } from 'react';
import classes from '../styles/mfaSettings.module.css';
import styles from '../styles/settings.module.css';
import { useNavigate } from 'react-router-dom';

const MfaSettings = () => {
  const [securityLevel, setSecurityLevel] = useState(1);
  const navigate = useNavigate();

  useEffect(() => {
    const savedLevel = localStorage.getItem('mfaSecurityLevel');
    if (savedLevel) {
      setSecurityLevel(parseInt(savedLevel));
    }
  }, []);

  const goMfa = () => {
    navigate('/settings');
  };

  const handleLevelChange = (e) => {
    const level = parseInt(e.target.value);
    setSecurityLevel(level);
    localStorage.setItem('mfaSecurityLevel', level);
  };

  return (
    <div className={classes.container}>
      <h3 className={classes.title}>MFA Settings</h3>

      <label className={classes.dropdownLabel}>
        Required Methods:
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

      <h3 className={styles.back} onClick={goMfa}>Back</h3>
    </div>
  );
};

export default MfaSettings;
