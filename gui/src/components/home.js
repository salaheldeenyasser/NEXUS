import classes from '../styles/home.module.css';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Home() {

    const [camError, setCamError] = useState(true);
    const navigate = useNavigate();


     const goToSettings = () => {
         navigate('/admin-pin-prompt');
     }


    return(
        <div>
            {camError ? (
                <img className={classes.camView} alt='fallback' src="/media/remove-user.png"/>
            ) : (
                <img className={classes.camView} onError={() => setCamError(true)} alt='camView' src="http://localhost:8080/stream.mjpg"/>
            )}
            <div className={classes.iconsContainer}>
                <img src="/media/yesVideo.png" onClick={() => setCamError(false)} alt="yesVideo" />
                <img src="/media/settings.png" onClick={goToSettings} alt="settings" />
                <img src="/media/noVideo.png" onClick={() => setCamError(true)} alt="noVideo" />
            </div>
        </div>
    )
}
