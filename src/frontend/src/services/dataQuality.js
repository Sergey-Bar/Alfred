// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Scaffold a frontend service for Data Quality Monitoring API endpoints.
// Why: Enables the React dashboard to report, retrieve, and display data quality events and alerts.
// Root Cause: No frontend integration existed for the new backend API.
// Context: This service provides methods for posting events, fetching all events, and fetching high-severity alerts. Future: add error handling, persistent storage, and advanced filtering. For advanced analytics, consider using a more advanced model (Claude Opus).

import axios from 'axios';

const API_BASE = '/api';

export const reportDataQualityEvent = async (event) => {
    const res = await axios.post(`${API_BASE}/data-quality/events`, event);
    return res.data;
};

export const getDataQualityEvents = async (dataset) => {
    const url = dataset ? `${API_BASE}/data-quality/events?dataset=${encodeURIComponent(dataset)}` : `${API_BASE}/data-quality/events`;
    const res = await axios.get(url);
    return res.data;
};

export const getHighSeverityAlerts = async () => {
    const res = await axios.get(`${API_BASE}/data-quality/alerts`);
    return res.data;
};
