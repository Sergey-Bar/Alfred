
// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Provides a global React context for theme (dark mode only) across the app. Always enforces dark mode for Alfred branding.
// Why: Centralizes theme logic and ensures consistent UI experience.
// Root Cause: Scattered theme logic leads to inconsistent look and feel.
// Context: All theme toggling and detection should use this context. Future: add light mode if needed.
// Model Suitability: For React context patterns, GPT-4.1 is sufficient.
import { createContext, useContext, useEffect } from 'react';

const ThemeContext = createContext();


// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: ThemeProvider always enables dark mode and exposes a no-op toggle for future extensibility.
// Why: Ensures Alfred's UI is always in dark mode for branding and accessibility.
// Root Cause: Allowing light mode would break design consistency.
// Context: Wrap the app in this provider to enforce dark mode.
export function ThemeProvider({ children }) {
    const darkMode = true;

    useEffect(() => {
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


// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Custom hook for accessing theme context.
// Why: Simplifies theme access for components.
// Root Cause: Direct context usage is verbose and error-prone.
// Context: Use in any component needing theme info.
export function useTheme() {
    return useContext(ThemeContext);
}
