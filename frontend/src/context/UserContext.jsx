import { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const UserContext = createContext(null);

export function UserProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchCurrentUser = async () => {
        if (!api.isAuthenticated()) {
            setUser(null);
            setLoading(false);
            return;
        }

        try {
            // Try to get user info from overview or dedicated endpoint
            const overview = await api.getOverview();

            // Get current user from stored info or create from overview
            const storedUser = localStorage.getItem('alfred_current_user');
            if (storedUser) {
                setUser(JSON.parse(storedUser));
            } else {
                // Default admin user info
                const defaultUser = {
                    id: 'admin',
                    name: 'Administrator',
                    email: 'admin@alfred.local',
                    role: 'admin',
                    personal_quota: 50000,
                    used_tokens: overview?.total_tokens_used || 0,
                    team: 'System Administrators',
                    avatar: null,
                    created_at: new Date().toISOString(),
                    last_login: new Date().toISOString(),
                };
                setUser(defaultUser);
                localStorage.setItem('alfred_current_user', JSON.stringify(defaultUser));
            }
        } catch (err) {
            console.error('Failed to fetch user info:', err);
            // Use minimal fallback
            setUser({
                id: 'unknown',
                name: 'User',
                email: 'user@alfred.local',
                role: 'user',
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCurrentUser();
    }, []);

    const updateUser = (updates) => {
        const updatedUser = { ...user, ...updates };
        setUser(updatedUser);
        localStorage.setItem('alfred_current_user', JSON.stringify(updatedUser));
    };

    const clearUser = () => {
        setUser(null);
        localStorage.removeItem('alfred_current_user');
    };

    return (
        <UserContext.Provider value={{ user, loading, updateUser, clearUser, refetch: fetchCurrentUser }}>
            {children}
        </UserContext.Provider>
    );
}

export function useUser() {
    const context = useContext(UserContext);
    if (!context) {
        throw new Error('useUser must be used within a UserProvider');
    }
    return context;
}
