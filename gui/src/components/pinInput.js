import { useEffect, useRef } from 'react';
import classes from '../styles/pinInput.module.css';
import { useNavigate } from 'react-router-dom';

export default function PinInput() {
    
    const inputRef = useRef(null);
    const navigate = useNavigate();


    const goToCamView = () => {
         navigate('/cam-view');
        
    }

    const goToSettings = () => {
        navigate('/settings');
    }

    useEffect(() => {
        inputRef.current?.focus();
    }, []);
    

    return(
        <div>
            <input type="password" name="pinInput" ref={inputRef} placeholder='Enter the PIN' className={classes.pinInput} />
            <button onClick={goToCamView} className={classes.camAccess}>Access Camera</button>
            <button onClick={goToSettings} className={classes.settingsBtn}>Settings</button>
        </div>
    )
}
