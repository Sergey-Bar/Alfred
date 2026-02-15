// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Service for Data Access Controls API. Provides methods to create, list, get, delete policies, and check access for users/resources.
// Why: Enables frontend admin UI to manage fine-grained data access controls for sensitive/PII data.
// Root Cause: No frontend integration for new backend data access API.
// Context: Used by admin/config UI for privacy/compliance. Future: extend for dynamic policy engines, audit logging, and attribute-based access.
// Model Suitability: GPT-4.1 is suitable for REST API service patterns; for advanced policy logic, consider Claude 3 or Gemini 1.5.

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
