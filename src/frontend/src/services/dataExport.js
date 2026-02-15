// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Provides a frontend service stub for exporting analytics data from the backend.
// Why: Enables programmatic access to analytics data for external tools and partners.
// Root Cause: No API integration for data export existed.
// Context: Extend this service to support more formats and filtering.
// Model Suitability: For advanced export workflows, consider GPT-4 Turbo or Claude Sonnet.

import api from './api';

export async function exportAnalytics(format = 'csv') {
    // Fetches analytics data in the specified format (csv or json)
    const res = await api.get('/export/analytics', { params: { format } });
    return res.data;
}
