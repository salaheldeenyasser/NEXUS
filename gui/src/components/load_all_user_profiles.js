import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

function TestUserProfiles() {
  const [userProfiles, setUserProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:8000/users/users/')
      .then(response => response.json())
      .then(data => {
        setUserProfiles(data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching user profiles:', error);
        setLoading(false);
      });
  }, []);

  const goBack = () => {
    navigate('/');
  };

  return (
    <div>
      <h3>
        {loading
          ? 'Loading user profiles...'
          : `Fetched ${userProfiles.length} user profiles`}
      </h3>
      <h3 onClick={goBack} style={{ cursor: 'pointer' }}>
        Back
      </h3>
    </div>
  );
}

export default TestUserProfiles;
