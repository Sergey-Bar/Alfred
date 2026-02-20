/**
 * Suitability: Simple config file, L1 model appropriate
 */

/**
 * Application version - update this when releasing new versions
 */
export const APP_VERSION = '1.0.0';

/**
 * Full version string with app name
 */
export const VERSION_STRING = `Alfred v${APP_VERSION}`;

/**
 * Build info displayed in footer
 */
export const BUILD_INFO = `${VERSION_STRING} | Built with React + Vite + TailwindCSS`;

/**
 * API configuration
 */
export const API_CONFIG = {
    baseUrl: import.meta.env.VITE_API_URL || '/api',
    timeout: 30000,
};

export default {
    APP_VERSION,
    VERSION_STRING,
    BUILD_INFO,
    API_CONFIG,
};
