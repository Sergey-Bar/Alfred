// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Service for Data Anonymization & Masking API. Methods to create, list, get, delete policies, and preview masked data for privacy-preserving analytics.
// Why: Enables frontend admin UI to manage anonymization/masking for sensitive/PII data.
// Root Cause: No frontend integration for new backend anonymization API.
// Context: Used by admin/config UI for privacy/compliance. Future: extend for dynamic masking, audit logging, and attribute-based policies.
// Model Suitability: GPT-4.1 is suitable for REST API service patterns; for advanced privacy logic, consider Claude 3 or Gemini 1.5.

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
