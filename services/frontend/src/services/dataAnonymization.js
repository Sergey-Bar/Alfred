import axios from 'axios';

const BASE_URL = '/v1/data_anonymization';

const DataAnonymizationService = {
    createPolicy: (payload) => axios.post(`${BASE_URL}/policies`, payload),
    listPolicies: () => axios.get(`${BASE_URL}/policies`),
    getPolicy: (policyId) => axios.get(`${BASE_URL}/policies/${policyId}`),
    deletePolicy: (policyId) => axios.delete(`${BASE_URL}/policies/${policyId}`),
    previewMaskedData: (payload) => axios.post(`${BASE_URL}/preview_masked_data`, payload),
};

export default DataAnonymizationService;
