import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import classes from '../styles/fingerprintPage.module.css';

const FingerprintPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { id } = location.state || {};

  const isEditing = Boolean(id);
  const [profile, setProfile] = useState(null);
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      if (isEditing) {
        try {
          const res = await fetch(`http://localhost:8000/users/profiles/${id}`);
          const data = await res.json();
          setProfile(data);
        } catch (err) {
          setMessage('Failed to load profile');
        }
      }
    };

    fetchProfile();
  }, [id, isEditing]);

  const enroll = async () => {
    setIsLoading(true);
    setMessage('Enrolling...');

    try {
      const fingerprint_embedding = 'mock_fingerprint_embedding';

      if (isEditing && profile) {
        const response = await fetch(`http://localhost:8000/users/profiles/${id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fingerprint_embedding }),
        });

        const result = await response.json();

        if (response.ok) {
          setMessage('Fingerprint updated!');
        } else {
          setMessage('Failed to update fingerprint: ' + result.detail);
        }

        setTimeout(() => {
          navigate(`/settings/profile-choice-menu/manage-profiles/edit-profile/${id}`);
        }, 1500);
      } else {
        const response = await fetch('http://localhost:8000/access/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fingerprint_result: 'enroll' }),
        });

        const data = await response.json();
        setMessage(data.message);
      }
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const authenticate = async () => {
    setIsLoading(true);
    setMessage('Authenticating...');

    try {
      const response = await fetch('http://localhost:8000/access/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fingerprint_result: 'authenticate' }),
      });

      const data = await response.json();
      setMessage(data.message);
    } catch (err) {
      setMessage(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const goHome = () => {
    if (isEditing) {
      navigate(`/settings/profile-choice-menu/manage-profiles/edit-profile/${id}`);
    } else {
      navigate('/settings');
    }
  };

  if (isEditing && !profile) {
    return <p className="p-6">Loading profile...</p>;
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">Fingerprint Access</h1>
      <div className="flex gap-4">
        <button
          onClick={enroll}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow"
          disabled={isLoading}
        >
          {isLoading ? 'Enrolling...' : isEditing ? 'Retake Fingerprint' : 'Enroll Fingerprint'}
        </button>

        <button
          onClick={authenticate}
          className="bg-green-600 text-white px-4 py-2 rounded-lg shadow"
          disabled={isLoading}
        >
          {isLoading ? 'Authenticating...' : 'Authenticate'}
        </button>

        {!isEditing && (
          <button
            onClick={() =>
              navigate('/settings/profile-choice-menu/add-profile/face', {
                state: { fingerprint_embedding: 'mock_fingerprint_embedding' },
              })
            }
            className="bg-purple-600 text-white px-4 py-2 rounded-lg shadow"
            disabled={isLoading}
          >
            Next
          </button>
        )}
      </div>

      <p className="mt-4">{message}</p>
      <h3 className={classes.back} onClick={goHome}>
        Back
      </h3>
    </div>
  );
};

export default FingerprintPage;
