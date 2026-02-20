import axios from 'axios';

const BASE_URL = '/v1/data_access';

const DataAccessService = {
    createPolicy: (payload) => axios.post(`${BASE_URL}/policies`, payload),
    listPolicies: () => axios.get(`${BASE_URL}/policies`),
    getPolicy: (policyId) => axios.get(`${BASE_URL}/policies/${policyId}`),
    deletePolicy: (policyId) => axios.delete(`${BASE_URL}/policies/${policyId}`),
    checkAccess: (payload) => axios.post(`${BASE_URL}/check_access`, payload),
};

export default DataAccessService;
