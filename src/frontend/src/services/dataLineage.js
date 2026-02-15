// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Scaffold a frontend service for Data Lineage & Provenance API endpoints.
// Why: Enables the React dashboard to record, retrieve, and trace data lineage events.
// Root Cause: No frontend integration existed for the new backend API.
// Context: This service provides methods for posting lineage events, fetching all events, and tracing data origins. Future: add error handling, persistent storage, and graph visualization. For advanced lineage analytics, consider using a more advanced model (Claude Opus).

import axios from 'axios';

const API_BASE = '/api';

export const recordLineageEvent = async (event) => {
    try {
        const res = await axios.post(`${API_BASE}/data-lineage/events`, event);
        return res.data;
    } catch (error) {
        console.error('Error recording lineage event:', error);
        throw new Error('Failed to record lineage event. Please try again later.');
    }
};

export const getLineageEvents = async (dataset) => {
    // Added dataset parameter validation
    if (dataset && typeof dataset !== 'string') {
        throw new Error('Invalid dataset parameter. It must be a string.');
    }

    try {
        const url = dataset ? `${API_BASE}/data-lineage/events?dataset=${encodeURIComponent(dataset)}` : `${API_BASE}/data-lineage/events`;
        const res = await axios.get(url);
        return res.data;
    } catch (error) {
        console.error('Error fetching lineage events:', error);
        throw new Error('Failed to fetch lineage events. Please try again later.');
    }
};

export const traceDataOrigin = async (dataset) => {
    // Added validation for dataset existence
    if (!dataset) {
        throw new Error('Dataset parameter is required.');
    }

    try {
        const res = await axios.get(`${API_BASE}/data-lineage/trace?dataset=${encodeURIComponent(dataset)}`);
        return res.data;
    } catch (error) {
        console.error('Error tracing data origin:', error);
        throw new Error('Failed to trace data origin. Please try again later.');
    }
};
