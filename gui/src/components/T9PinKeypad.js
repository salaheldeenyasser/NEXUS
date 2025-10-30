import { useState, useEffect } from 'react';
import classes from '../styles/T9NameKeypad.module.css'; // Reuses the same CSS

const keys = [
  { key: '1', label: '1' },
  { key: '2', label: '2' },
  { key: '3', label: '3' },
  { key: '4', label: '4' },
  { key: '5', label: '5' },
  { key: '6', label: '6' },
  { key: '7', label: '7' },
  { key: '8', label: '8' },
  { key: '9', label: '9' },
  { key: 'back', label: '←' },
  { key: '0', label: '0' },
  { key: 'confirm', label: '✔' },
];

export default function T9PinKeypad({ onConfirm, onCancel }) {
  const [typed, setTyped] = useState('');

  const handleKeyPress = (key) => {
    if (key === 'back') {
      setTyped((prev) => prev.slice(0, -1));
    } else if (key === 'confirm') {
      //if (typed.length === 0) return; // prevent submitting empty PIN
      console.log('Confirming PIN:', typed); // debug log
      onConfirm(typed);
    } else {
      setTyped((prev) => prev + key);
    }
  };

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onCancel();
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onCancel]);

  return (
    <div className={classes.outerContainer}>
      <div className={classes.overlay}>
        <div className={classes.keypadContainer}>
          <div className={classes.inputDisplay}>
            {typed.length > 0 ? '●'.repeat(typed.length) : 'Enter PIN'}
          </div>
          <div className={classes.buttonGrid}>
            {keys.map(({ key, label }) => (
              <button
                key={key}
                className={classes.keyButton}
                onClick={() => handleKeyPress(key)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
