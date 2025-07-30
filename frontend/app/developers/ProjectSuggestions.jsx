'use client';
import { useEffect, useState } from 'react';

export default function ProjectSuggestions({ developerId }) {
  const [projects, setProjects] = useState([]);

  useEffect(() => {
    fetch(`https://your-backend-api.com/api/developers/${developerId}/suggested-projects/`)
      .then(res => res.json())
      .then(setProjects);
  }, [developerId]);

  const applyToProject = async (projectId) => {
    await fetch(`https://your-backend-api.com/api/projects/${projectId}/apply/`, {
      method: 'POST',
      credentials: 'include'
    });
    alert('Başvuru yapıldı!');
  };

  return (
    <section>
      <h2>Önerilen Projeler</h2>
      <ul>
        {projects.map(proj => (
          <li key={proj.id} style={{ marginBottom: 12 }}>
            <strong>{proj.title}</strong> - {proj.description}
            <button style={{ marginLeft: 8 }} onClick={() => applyToProject(proj.id)}>Katıl</button>
          </li>
        ))}
      </ul>
    </section>
  );
}
