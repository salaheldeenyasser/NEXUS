import { useNavigate } from 'react-router-dom';
import classes from '../styles/resetSystem.module.css';

export default function ResetSystem() {

    const navigate = useNavigate();

    const resetSystem = async () => {
        try {
            const res = await fetch('http://localhost:8000/gui/reset_system', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({}),
            });

            const data = await res.json();

            navigate('/create-admin');

            if (res.ok && data.success) {
                navigate('/create-admin');
            } else {
                console.error('Reset failed:', data.error || 'Unknown error');
            }
        } catch (error) {
            console.error('Error resetting system:', error);
        }
    };

    const goSysSettings = () => {
        navigate('/settings/system-settings');
    };

    return (
        <div className={classes.ulSys}>
            <ul>
                <li className={classes.liSys} onClick={resetSystem}>Confirm</li>
                <li className={classes.liSys} onClick={goSysSettings}>Cancel</li>
            </ul>
        </div>
    );
}
