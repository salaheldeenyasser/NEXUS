import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import classes from '../styles/systemSettings.module.css';
import Switch from '@mui/material/Switch';
import { FormGroup, FormControlLabel } from '@mui/material';

export default function SystemSettings() {
  const navigate = useNavigate();
  const [muted, setMuted] = useState(false);
  const [lockEngaged, setLockEngaged] = useState(true);

  // Fetch settings from backend on mount
  useEffect(() => {
    fetch('http://localhost:8000/settings/system-settings')
      .then((res) => res.json())
      .then((data) => {
        if (data.mute !== undefined) {
          setMuted(data.mute);
        }
        if (data.lock_engaged !== undefined) {
          setLockEngaged(data.lock_engaged);
        }
      })
      .catch((err) => {
        console.error('Failed to fetch system settings:', err);
      });
  }, []);

  const goSettings = () => {
    navigate('/settings');
  };

  const goReset = () => {
    navigate('/settings/system-settings/reset-system');
  };

  const toggleMute = async () => {
    const newMuted = !muted;
    setMuted(newMuted);

    try {
      await fetch('http://localhost:8000/settings/system-settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mute: newMuted }),
      });

      if (newMuted) {
        await window.pywebview.api.mute_device();
      } else {
        await window.pywebview.api.unmute_device();
      }
    } catch (err) {
      console.error('Mute toggle failed:', err);
    }
  };

  // const toggleLock = async () => {
  //   const newState = !lockEngaged;
  //   setLockEngaged(newState);

  //   try {
  //     await fetch('http://localhost:8000/settings/system-settings', {
  //       method: 'POST',
  //       headers: { 'Content-Type': 'application/json' },
  //       body: JSON.stringify({ lock_engaged: newState }),
  //     });

  //     if (window.pywebview?.api?.toggle_lock) {
  //       await window.pywebview.api.toggle_lock(newState);
  //     }
  //   } catch (err) {
  //     console.error('Error toggling lock:', err);
  //   }
  // };

  const goChange = () => {
    navigate('/settings/change-pin');
  }

  return (
    <div>
      <ul className={classes.ulSysSettings}>
      <li className={classes.liSysSettings} onClick={goChange}>Change PIN</li>
        <li className={classes.liSysSettings}>
          <FormGroup>
            <FormControlLabel
              className={classes.switch}
              control={
                <Switch
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#4caf50',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#4caf50',
                    },
                  }}
                  checked={muted}
                  onChange={toggleMute}
                />
              }
              label="Mute Device"
            />
          </FormGroup>
        </li>
        {/* <li className={classes.liSysSettings}>
          <FormGroup>
            <FormControlLabel
              className={classes.switch}
              control={
                <Switch
                  sx={{
                    '& .MuiSwitch-switchBase.Mui-checked': {
                      color: '#4caf50',
                    },
                    '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                      backgroundColor: '#4caf50',
                    },
                  }}
                  checked={lockEngaged}
                  onChange={toggleLock}
                />
              }
              label={lockEngaged ? 'Locked' : 'Unlocked'}
            />
          </FormGroup>
        </li> */}
        <li className={classes.liSysSettings} onClick={goReset}>Reset System</li>
      </ul>
      <h3 className={classes.back} onClick={goSettings}>Back</h3>
    </div>
  );
}