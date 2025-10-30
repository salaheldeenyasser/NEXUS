// Loader.js
import { useEffect, useState } from 'react';
import CreateAdmin from './createAdmin';
import Home from './home';

export default function Loader() {
  const [profiles, setProfiles] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfiles = async () => {
      try {
        const res = await fetch('http://localhost:8000/users/profiles');
        if (!res.ok) {
          throw new Error('Failed to fetch profiles');
        }
        const data = await res.json();
        setProfiles(data);
      } catch (error) {
        console.error('Error fetching profiles:', error);
        setProfiles([]);
      } finally {
        setLoading(false);
      }
    };

    fetchProfiles();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return profiles.length === 0 ? <CreateAdmin /> : <Home />;
}
