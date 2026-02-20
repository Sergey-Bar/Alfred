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
