import { createContext, useContext, useEffect } from 'react';

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
    // Always dark mode - Alfred from Batman style
    const darkMode = true;

    useEffect(() => {
        // Always apply dark mode
        document.documentElement.classList.add('dark');
    }, []);

    const toggleDarkMode = () => {
        // No-op - dark mode is permanent
    };

    return (
        <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
            {children}
        </ThemeContext.Provider>
    );
}

export function useTheme() {
    return useContext(ThemeContext);
}
