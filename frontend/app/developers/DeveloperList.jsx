'use client';
import { useEffect, useState } from 'react';

export default function DeveloperList() {
  const [developers, setDevelopers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Örnek veri, gerçek API ile değiştirilebilir
    setTimeout(() => {
      setDevelopers([
        { id: 1, name: "Ali Veli", skills: ["React", "Node.js"], github: "#", linkedin: "#" },
        { id: 2, name: "Ayşe Yılmaz", skills: ["Python", "Django"], github: "#", linkedin: "#" },
        { id: 3, name: "Mehmet Can", skills: ["Java", "Spring"], github: "#", linkedin: "#" },
      ]);
      setLoading(false);
    }, 500);
  }, []);

  if (loading) return <div>Yükleniyor...</div>;

  return (
    <section>
      <h2>Tüm Geliştiriciler</h2>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 16 }}>
        {developers.map((dev) => (
          <div key={dev.id} style={{ border: "1px solid #eee", padding: 16, borderRadius: 8 }}>
            <h3>{dev.name}</h3>
            <p>Beceriler: {dev.skills.join(", ")}</p>
            <a href={dev.github} target="_blank">GitHub</a> | <a href={dev.linkedin} target="_blank">LinkedIn</a>
          </div>
        ))}
      </div>
    </section>
  );
}
