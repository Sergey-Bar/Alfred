// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Provides a frontend service stub for fetching KPI/metric definitions from the backend.
// Why: Enables the dashboard and analytics UI to display available business metrics.
// Root Cause: No API integration for metrics existed.
// Context: Extend this service to fetch live metric values and support custom metrics.
// Model Suitability: For advanced analytics UI, consider GPT-4 Turbo or Claude Sonnet.

import api from './api';

export async function fetchKpis() {
    // Fetches predefined KPIs from the backend
    const res = await api.get('/metrics/kpis');
    return res.data;
}
