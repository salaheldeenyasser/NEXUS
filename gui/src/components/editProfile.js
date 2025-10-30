import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import classes from '../styles/selectProfile.module.css';

export default function EditProfile() {
  const { id } = useParams();
  const [profile, setProfile] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://localhost:8000/users/profiles")
      .then(res => res.json())
      .then(data => {
        const match = data.find(p => p.id === id);
        setProfile(match);
      });
  }, [id]);

  const goBack = () => {
    navigate('/settings/profile-choice-menu/manage-profiles');
  };

  const handleFaceScan = () => {
    navigate('/settings/profile-choice-menu/add-profile/face', {
      state: {
        id: profile.id
      }
    });
  };

  const handleFingerprintScan = () => {
  navigate('/settings/profile-choice-menu/add-profile/fingerprint', {
    state: { id: profile.id }
    });
  };


  if (!profile) return <p>Loading...</p>;

  return (
    <div>
      <h2 style={{ textAlign: 'center', marginTop: '20px' }}>Edit Profile</h2>
      <div style={{ height: '60vh', overflowY: 'auto' }}>
        <ul className={classes.ulProfCho}>
          <li
          className={classes.liProfCho}
          onClick={() =>
              navigate(`/settings/profile-choice-menu/manage-profiles/${id}/change-role`, {
              state: { id: profile.id, currentRole: profile.role }
              })
          }
          >
          Change Role
          </li>

          <li className={classes.liProfCho} onClick={handleFingerprintScan}>Retake Fingerprint Scan</li>
          <li className={classes.liProfCho} onClick={handleFaceScan}>Retake Face Scan</li>
          {profile.role === "admin" && (
            <li
              className={classes.liProfCho}
              onClick={() =>
                navigate(`/settings/profile-choice-menu/manage-profiles/${id}/change-admin-pin`, {
                  state: { id: profile.id }
                })
              }
            >
              Change Admin PIN
            </li>
          )}
          <li className={classes.liProfCho} onClick={() =>
              navigate(`/settings/profile-choice-menu/manage-profiles/${id}/confirm-delete`, {
              state: { id: profile.id }
              })
          }>Delete Profile</li>
        </ul>
      </div>
      <h3 className={classes.back} onClick={goBack}>Back</h3>
    </div>
  );
}