import { useState, useRef } from 'react';
import classes from '../styles/T9NameKeypad.module.css';

const t9Map = {
  '1': [''],
  '2': ['a', 'b', 'c'],
  '3': ['d', 'e', 'f'],
  '4': ['g', 'h', 'i'],
  '5': ['j', 'k', 'l'],
  '6': ['m', 'n', 'o'],
  '7': ['p', 'q', 'r', 's'],
  '8': ['t', 'u', 'v'],
  '9': ['w', 'x', 'y', 'z'],
  '0': [' '],
};

const keys = [
  { key: '1', label: '1' },
  { key: '2', label: '2\nabc' },
  { key: '3', label: '3\ndef' },
  { key: '4', label: '4\nghi' },
  { key: '5', label: '5\njkl' },
  { key: '6', label: '6\nmno' },
  { key: '7', label: '7\npqrs' },
  { key: '8', label: '8\ntuv' },
  { key: '9', label: '9\nwxyz' },
  { key: 'back', label: '←' },
  { key: '0', label: '0\nSpace' },
  { key: 'confirm', label: '✔' },
];

export default function T9NameKeypad({ onConfirm }) {
  const [typed, setTyped] = useState('');
  const [preview, setPreview] = useState('');
  const currentKeyRef = useRef('');
  const pressIndexRef = useRef(0);
  const timeoutRef = useRef(null);

  const finalizePreview = () => {
    const currentKey = currentKeyRef.current;
    const pressIndex = pressIndexRef.current;
    const letters = t9Map[currentKey];
    if (letters && letters.length > 0) {
      setTyped(prev => prev + letters[pressIndex % letters.length]);
    }
    setPreview('');
    currentKeyRef.current = '';
    pressIndexRef.current = 0;
    clearTimeout(timeoutRef.current);
  };

  const startCycle = (key) => {
    currentKeyRef.current = key;
    pressIndexRef.current = 0;
    setPreview(t9Map[key][0]);
    timeoutRef.current = setTimeout(finalizePreview, 1000);
  };

  const cycleCharacter = () => {
    const key = currentKeyRef.current;
    const letters = t9Map[key];
    pressIndexRef.current = (pressIndexRef.current + 1) % letters.length;
    setPreview(letters[pressIndexRef.current]);
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(finalizePreview, 1000);
  };

  const handleKeyPress = (key) => {
    if (key === 'back') {
      finalizePreview();
      setTyped(prev => prev.slice(0, -1));
      return;
    }
  
    if (key === 'confirm') {
      finalizePreview(); // <-- Ensure the previewed character is added
      onConfirm(typed + preview); // <-- Use updated value
      setTyped(''); // Optionally clear after confirming
      setPreview('');
      return;
    }
  
    if (key !== currentKeyRef.current) {
      finalizePreview();
      if (t9Map[key] && t9Map[key].length > 0) {
        startCycle(key);
      }
    } else {
      cycleCharacter();
    }
  };
  

  return (
    <div className={classes.outerContainer}>
      <div className={classes.overlay}>
        <div className={classes.keypadContainer}>
          <div className={classes.inputDisplay}>{typed + preview}</div>
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
