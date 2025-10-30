import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import classes from '../styles/selectProfile.module.css';

export default function SelectProfile() {
  const [profiles, setProfiles] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://localhost:8000/users/profiles")
        .then(res => res.json())
        .then(data => {
        console.log("Profiles response:", data);
        setProfiles(data);
    })
        .catch(err => {
        console.error("Failed to load profiles:", err);
    });
    }, []);

  const goBack = () => {
    navigate('/settings/profile-choice-menu');
  };

  const capitalizeFirstLetter = (string) => {
    return string.charAt(0).toUpperCase() + string.slice(1);
  };

  return (
    <div>
      <h2 style={{ textAlign: 'center', marginTop: '20px' }}>Select Profile</h2>
      <ul className={classes.ulProfCho}>
      {profiles.map((profile) => (
      <li
        key={profile.id}
        className={classes.liProfCho}
        onClick={() => navigate(`/settings/profile-choice-menu/manage-profiles/edit-profile/${profile.id}`)}
      >
        {profile.name} — {capitalizeFirstLetter(profile.role)}
      </li>
      ))}
      </ul>
      <h3 className={classes.back} onClick={goBack}>Back</h3>
    </div>
  );
}