import { useEffect, useState } from 'react';
import api from '../services/api';

export default function NotificationCenter({ isAdmin = false }) {
    const [feed, setFeed] = useState([]);
    const [channels, setChannels] = useState([]);
    const [newChannel, setNewChannel] = useState('');
    const [message, setMessage] = useState('');
    const [sendPayload, setSendPayload] = useState('');

    useEffect(() => {
        fetchFeed();
        if (isAdmin) fetchChannels();
    }, [isAdmin]);

    async function fetchFeed() {
        setFeed(await api.getUserNotifications());
    }
    async function fetchChannels() {
        setChannels(await api.getNotificationChannels());
    }
    async function handleAddChannel() {
        if (!newChannel) return;
        await api.addNotificationChannel({ name: newChannel });
        setNewChannel('');
        fetchChannels();
        setMessage('Channel added');
    }
    async function handleDeleteChannel(id) {
        await api.deleteNotificationChannel(id);
        fetchChannels();
        setMessage('Channel deleted');
    }
    async function handleTestChannel(id) {
        await api.testNotificationChannel(id);
        setMessage('Test notification sent');
    }
    async function handleSendNotification() {
        if (!sendPayload) return;
        await api.sendNotification({ message: sendPayload });
        setSendPayload('');
        setMessage('Notification sent');
    }

    return (
        <div style={{ padding: 24 }}>
            <h2>Notification Center</h2>
            {message && <div style={{ color: 'green', marginBottom: 8 }}>{message}</div>}
            <div>
                <h3>Your Notifications</h3>
                <ul>
                    {feed.map((n, i) => (
                        <li key={i}>{n.message || n.text || JSON.stringify(n)}</li>
                    ))}
                </ul>
            </div>
            {isAdmin && (
                <div style={{ marginTop: 32 }}>
                    <h3>Notification Channels</h3>
                    <ul>
                        {channels.map(c => (
                            <li key={c.id || c.name}>
                                {c.name || c.id}
                                <button onClick={() => handleTestChannel(c.id || c.name)}>Test</button>
                                <button onClick={() => handleDeleteChannel(c.id || c.name)}>Delete</button>
                            </li>
                        ))}
                    </ul>
                    <input value={newChannel} onChange={e => setNewChannel(e.target.value)} placeholder="New channel name" />
                    <button onClick={handleAddChannel}>Add Channel</button>
                    <div style={{ marginTop: 16 }}>
                        <h4>Send Notification</h4>
                        <input value={sendPayload} onChange={e => setSendPayload(e.target.value)} placeholder="Message" />
                        <button onClick={handleSendNotification}>Send</button>
                    </div>
                </div>
            )}
        </div>
    );
}
