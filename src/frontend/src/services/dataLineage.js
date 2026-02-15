// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Scaffold a frontend service for Data Lineage & Provenance API endpoints.
// Why: Enables the React dashboard to record, retrieve, and trace data lineage events.
// Root Cause: No frontend integration existed for the new backend API.
// Context: This service provides methods for posting lineage events, fetching all events, and tracing data origins. Future: add error handling, persistent storage, and graph visualization. For advanced lineage analytics, consider using a more advanced model (Claude Opus).

import axios from 'axios';

const API_BASE = '/api';

export const recordLineageEvent = async (event) => {
    const res = await axios.post(`${API_BASE}/data-lineage/events`, event);
    return res.data;
};

export const getLineageEvents = async (dataset) => {
    const url = dataset ? `${API_BASE}/data-lineage/events?dataset=${encodeURIComponent(dataset)}` : `${API_BASE}/data-lineage/events`;
    const res = await axios.get(url);
    return res.data;
};

export const traceDataOrigin = async (dataset) => {
    const res = await axios.get(`${API_BASE}/data-lineage/trace?dataset=${encodeURIComponent(dataset)}`);
    return res.data;
};
