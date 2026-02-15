// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Provides a frontend service stub for fetching KPI/metric definitions from the backend.
// Why: Enables the dashboard and analytics UI to display available business metrics.
// Root Cause: No API integration for metrics existed.
// Context: Extend this service to fetch live metric values and support custom metrics.
// Model Suitability: For advanced analytics UI, consider GPT-4 Turbo or Claude Sonnet.

import api from './api';

export async function fetchKpis(page = 1, pageSize = 10) {
    // Fetches predefined KPIs from the backend
    try {
        const res = await api.get('/metrics/kpis', { params: { page, pageSize } });
        return res.data;
    } catch (error) {
        console.error('Error fetching KPIs:', error);
        throw new Error('Failed to fetch KPIs. Please try again later.');
    }
}
