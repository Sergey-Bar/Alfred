// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Scaffold a frontend service for Data Catalog & Metadata Management API endpoints.
// Why: Enables the React dashboard to register, list, and search datasets and their metadata.
// Root Cause: No frontend integration existed for the new backend API.
// Context: This service provides methods for registering datasets, listing all datasets, and searching by name/field. Future: add error handling, persistent storage, and advanced search. For advanced catalog features, consider using a more advanced model (Claude Opus).

import axios from 'axios';

const API_BASE = '/api';

export const registerDataset = async (dataset) => {
    const res = await axios.post(`${API_BASE}/data-catalog/datasets`, dataset);
    return res.data;
};

export const listDatasets = async () => {
    const res = await axios.get(`${API_BASE}/data-catalog/datasets`);
    return res.data;
};

export const searchDatasets = async (query) => {
    const res = await axios.get(`${API_BASE}/data-catalog/search?query=${encodeURIComponent(query)}`);
    return res.data;
};
