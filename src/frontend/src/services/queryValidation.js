// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Service for Advanced Query Validation & BI Integration API. Methods to validate queries and check BI integration compatibility.
// Why: Enables frontend admin/analyst UI to validate queries and check BI tool compatibility.
// Root Cause: No frontend integration for new backend query validation API.
// Context: Used by admin/analyst UI for query validation and BI integration. Future: extend for live query execution, schema introspection, and BI tool-specific validation.
// Model Suitability: GPT-4.1 is suitable for REST API service patterns; for advanced query analysis, consider Claude 3 or Gemini 1.5.

import axios from 'axios';

const BASE_URL = '/v1/query_validation';

const QueryValidationService = {
    validateQuery: (payload) => axios.post(`${BASE_URL}/validate`, payload),
    biIntegrationCheck: (payload) => axios.post(`${BASE_URL}/bi_check`, payload),
};

export default QueryValidationService;
