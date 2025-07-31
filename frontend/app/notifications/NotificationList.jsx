'use client';
import { useEffect, useState } from 'react';

export default function NotificationList() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Örnek veri, gerçek API ile değiştirilebilir
    setTimeout(() => {
      setNotifications([
        { id: 1, message: "Yeni bir proje eklendi!", date: "2025-07-30", read: false },
        { id: 2, message: "Profiliniz güncellendi.", date: "2025-07-29", read: true },
        { id: 3, message: "Birisi sizi takip etti.", date: "2025-07-28", read: false },
      ]);
      setLoading(false);
    }, 500);
  }, []);

  const markAsRead = (id) => {
    setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, read: true } : n));
  };

  if (loading) return <div>Yükleniyor...</div>;

  return (
    <section>
      <h2>Bildirimler</h2>
      <ul>
        {notifications.map((n) => (
          <li key={n.id} style={{ fontWeight: n.read ? "normal" : "bold", marginBottom: 10 }}>
            {n.message} <small style={{ marginLeft: 8 }}>{n.date}</small>
            {!n.read && <button style={{ marginLeft: 8 }} onClick={() => markAsRead(n.id)}>Okundu</button>}
          </li>
        ))}
      </ul>
    </section>
  );
}
