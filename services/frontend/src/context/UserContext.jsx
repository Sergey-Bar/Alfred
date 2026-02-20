
import { createContext, useContext, useEffect, useState } from 'react';
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
            const userData = await api.getCurrentUser();
            const quotaData = await api.getQuotaStatus();

            const fullUser = {
                ...userData,
                role: userData.is_admin ? 'admin' : 'user',
                personal_quota: quotaData.personal_quota,
                used_tokens: quotaData.used_tokens,
                available_quota: quotaData.available_quota,
                avatar: null,
            };
            setUser(fullUser);
        } catch (err) {
            console.error('Failed to fetch user info:', err);
            // If fetching fails, clear user — avoid relying on stale localStorage data
            setUser(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchCurrentUser();
    }, []);

    const updateUser = async (updates) => {
        // Optimistically update UI
        const updatedUser = { ...user, ...updates };
        setUser(updatedUser);

        // Persist allowed fields to backend (name, email, preferences)
        try {
            const payload = {};
            if (updates.name) payload.name = updates.name;
            if (updates.email) payload.email = updates.email;
            if (updates.preferences) payload.preferences = updates.preferences;

            if (Object.keys(payload).length > 0) {
                await api.updateProfile(payload);
            }
        } catch (err) {
            console.error('Failed to persist user updates:', err);
        }
    };

    const clearUser = () => {
        setUser(null);
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
