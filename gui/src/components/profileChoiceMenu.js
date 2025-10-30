import { useNavigate } from 'react-router-dom';
import classes from '../styles/profileChoiceMenu.module.css';

export default function ProfileChoiceMenu() {

    const navigate = useNavigate();

    const goManage = () => {
        navigate('/settings/profile-choice-menu/manage-profiles');
    };

    const goSettings = () => {
        navigate('/settings');
    };

    const goAddUser = () => {
        navigate('/settings/profile-choice-menu/add-profile');
    }

    const goAdmin = () => {
        navigate('/create-admin');
    }

    return(
        <div className={classes.ulProfCho}>
            <ul>
                <li className={classes.liProfCho} onClick={goAddUser}>Add Profile</li>
                <li className={classes.liProfCho} onClick={goManage}>Manage Profiles</li>
                {/* <li className={classes.liProfCho} onClick={goAdmin}>Create Admin</li> */}
            </ul>
            <h3 className={classes.back} onClick={goSettings}>Back</h3>
        </div>
    )
}
