import { useNavigate } from 'react-router-dom';
import classes from '../styles/profileAdded.module.css';

export default function ProfileAdded() {
  const navigate = useNavigate();

  const goBack = () => {
    navigate('/settings/profile-choice-menu/');
  };

  return (
    <div className={classes.container}>
      <h2 className={classes.heading}>Profile Added!</h2>
      <h3 className={classes.back} onClick={goBack}>Back to User Management</h3>
    </div>
  );
}
