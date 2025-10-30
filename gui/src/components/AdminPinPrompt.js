import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import T9PinKeypad from '../components/T9PinKeypad';
import classes from '../styles/adminPinPrompt.module.css';

export default function AdminPINPrompt() {
  const [message, setMessage] = useState('');
  const [showKeypad, setShowKeypad] = useState(false);
  const [success, setSuccess] = useState(false);
  const [enteredPin, setEnteredPin] = useState('');
  const navigate = useNavigate();

  const handleConfirm = async (enteredPin) => {
    console.log('handleConfirm called with PIN:', enteredPin); // 🔍 DEBUG

    try {
      const res = await axios.post('http://localhost:8000/admin/verify-pin', null, {
        params: { pin: enteredPin },
      });

      console.log('Server response:', res.data); // 🔍 DEBUG

      if (res.data.success) {
        setMessage('Access granted!');
        setSuccess(true);
        setShowKeypad(false);
        setTimeout(() => navigate('/settings/'), 1000);
      } else {
        setMessage('Incorrect PIN. Try again.');
        setShowKeypad(false);
      }
    } catch (err) {
      console.error('PIN verification error:', err); // 🔍 DEBUG
      setShowKeypad(false);
      setMessage('Server error while verifying PIN.');
    }

    setEnteredPin(enteredPin);
  };

  const handleCancel = () => {
    setShowKeypad(false);
    setMessage('PIN entry cancelled.');
  };

  const goBack = () => {
    navigate('/');
  };

  return (
    <div>
      <h2 style={{ textAlign: 'center' }}>Please Input the Admin PIN</h2>

      
      <input
        type="password"
        value={enteredPin}
        onFocus={() => setShowKeypad(true)}
        readOnly
        style={{
          textAlign: 'center',
          width: '200px',
          height: '40px',
          fontSize: '24px',
          marginLeft: '10px',
          marginTop: '10px',
          marginBottom: '10px'
        }}
      />

      {showKeypad ? (
        <T9PinKeypad onConfirm={handleConfirm} onCancel={handleCancel} />
      ) : success ? (
        <div>
            <p style={{ color: 'green', textAlign: 'center' }}>{message}</p>
            <h3 className={classes.back} onClick={goBack}>Back</h3>
        </div>
      ) : (
        <div>
            <p style={{ color: 'red', textAlign: 'center' }}>{message}</p>
            <h3 className={classes.back} onClick={goBack}>Back</h3>
        </div>
      )}

      {/* {message && (
        <p
          style={{
            color: message === 'Access granted!' ? 'green' : 'red',
            marginLeft: '10px',
            marginTop: '10px',
          }}
        >
          {message}
        </p>
      )} */}

      {/* {message && <p style={{ color: 'red' }}>{message}</p>} */}

      {!showKeypad && !success && (
        <h3 onClick={goBack} className={classes.back}>
          Back
        </h3>
      )}
    </div>
  );
}
