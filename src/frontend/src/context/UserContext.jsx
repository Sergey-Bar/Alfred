
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Provides a global React context for user identity, quota, and profile management. Handles fetch, update, and clear logic for the current user.
// Why: Centralizes user state and ensures all components have consistent access to user info.
// Root Cause: Scattered user logic leads to stale state and security issues.
// Context: All user/profile logic should use this provider and hook. Future: consider role-based access helpers.
// Model Suitability: For React context and user state, GPT-4.1 is sufficient.
import { createContext, useContext, useEffect, useState } from 'react';
import api from '../services/api';

const UserContext = createContext(null);

// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: UserProvider fetches, updates, and clears user state, exposing helpers and loading state.
// Why: Ensures user info is always fresh and up-to-date.
// Root Cause: Manual user state management is error-prone.
// Context: Wrap the app in this provider to enable user logic everywhere.
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


// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Custom hook for accessing user context and helpers.
// Why: Simplifies user state access in components.
// Root Cause: Direct context usage is verbose and error-prone.
// Context: Use in any component needing user info or actions.
export function useUser() {
    const context = useContext(UserContext);
    if (!context) {
        throw new Error('useUser must be used within a UserProvider');
    }
    return context;
}
