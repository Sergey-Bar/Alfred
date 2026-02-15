// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Provides a frontend service stub for fetching data usage analytics from the backend.
// Why: Enables the dashboard and analytics UI to display dataset usage, report popularity, and user engagement.
// Root Cause: No API integration for usage analytics existed.
// Context: Extend this service to support filtering, visualization, and user-specific analytics.
// Model Suitability: For advanced analytics UI, consider GPT-4 Turbo or Claude Sonnet.

import api from './api';

export async function fetchUsageAnalytics(period = '7d') {
    // Fetches usage analytics for the given period (7d, 30d, 90d)
    const res = await api.get('/analytics/usage', { params: { period } });
    return res.data;
}
