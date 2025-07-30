'use client';
import { useEffect, useState } from 'react';

export default function NotificationList() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    fetch('https://your-backend-api.com/api/notifications/', { credentials: 'include' })
      .then(res => res.json())
      .then(setNotifications);
  }, []);

  const markAsRead = async (id) => {
    await fetch(`https://your-backend-api.com/api/notifications/${id}/read/`, {
      method: 'POST',
      credentials: 'include'
    });
    setNotifications(notifications.map(n => n.id === id ? { ...n, read: true } : n));
  };

  return (
    <section>
      <ul>
        {notifications.map(n => (
          <li key={n.id} style={{ fontWeight: n.read ? 'normal' : 'bold', marginBottom: 10 }}>
            {n.message}
            {!n.read && <button style={{ marginLeft: 8 }} onClick={() => markAsRead(n.id)}>Okundu</button>}
          </li>
        ))}
      </ul>
    </section>
  );
}
