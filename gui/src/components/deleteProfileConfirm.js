import { useNavigate, useLocation } from 'react-router-dom';
import classes from '../styles/resetSystem.module.css';

export default function DeleteProfileConfirm() {
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = location.state || {};

  const handleDelete = async () => {
    try {
      const res = await fetch(`http://localhost:8000/gui/delete_user_profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: id }),
      });

      const data = await res.json();
      if (res.ok && data.success) {
        navigate('/settings/profile-choice-menu/manage-profiles');
      } else {
        console.error('Failed to delete profile:', data.error || 'Unknown error');
      }
    } catch (error) {
      console.error('Error deleting profile:', error);
    }
  };


  const handleCancel = () => {
    navigate(`/settings/profile-choice-menu/manage-profiles/edit-profile/${id}`);
  };

  return (
    <div className={classes.ulSys}>
      <h2 style={{textAlign: 'center', marginTop: '-20px'}}>Are You Sure?</h2>
      <ul>
        <li style={{textAlign: 'center'}} className={classes.liSys} onClick={handleDelete}>Yes</li>
        <li style={{textAlign: 'center'}} className={classes.liSys} onClick={handleCancel}>No</li>
      </ul>
    </div>
  );
}
