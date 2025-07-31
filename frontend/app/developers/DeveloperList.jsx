'use client';
import { useEffect, useState } from 'react';

export default function DeveloperList() {
  const [developers, setDevelopers] = useState([]);

  useEffect(() => {
    fetch('https://your-backend-api.com/api/developers/')
      .then(res => res.json())
      .then(setDevelopers);
  }, []);

  return (
    <section>
      <h2>Tüm Geliştiriciler</h2>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16 }}>
        {developers.map(dev => (
          <div key={dev.id} style={{ border: '1px solid #eee', padding: 16, borderRadius: 8 }}>
            <h3>{dev.name}</h3>
            <p>Beceriler: {dev.skills?.join(', ')}</p>
            <a href={dev.github} target="_blank">GitHub</a> | <a href={dev.linkedin} target="_blank">LinkedIn</a>
          </div>
        ))}
      </div>
    </section>
  );
}
