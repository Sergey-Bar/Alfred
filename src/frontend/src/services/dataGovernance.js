// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Scaffold a frontend service for Data Governance & Stewardship API endpoints.
// Why: Enables the React dashboard to register, list, and manage governance assignments and policies.
// Root Cause: No frontend integration existed for the new backend API.
// Context: This service provides methods for registering assignments/policies and listing them. Future: add error handling, persistent storage, and policy enforcement. For advanced governance logic, consider using a more advanced model (Claude Opus).

import axios from 'axios';

const API_BASE = '/api';

export const registerAssignment = async (assignment) => {
    const res = await axios.post(`${API_BASE}/data-governance/assignments`, assignment);
    return res.data;
};

export const listAssignments = async (dataset) => {
    const url = dataset ? `${API_BASE}/data-governance/assignments?dataset=${encodeURIComponent(dataset)}` : `${API_BASE}/data-governance/assignments`;
    const res = await axios.get(url);
    return res.data;
};

export const registerPolicy = async (policy) => {
    const res = await axios.post(`${API_BASE}/data-governance/policies`, policy);
    return res.data;
};

export const listPolicies = async () => {
    const res = await axios.get(`${API_BASE}/data-governance/policies`);
    return res.data;
};
