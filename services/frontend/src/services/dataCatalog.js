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
