// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Service for BI Tools Integration API. Methods to add, list, get, remove BI connectors, and test connections for Power BI, Tableau, Looker.
// Why: Enables frontend admin/config UI to manage BI tool integrations.
// Root Cause: No frontend integration for new backend BI connectors API.
// Context: Used by admin/config UI for analytics/reporting integration. Future: extend for OAuth, live sync, and connector health monitoring.
// Model Suitability: GPT-4.1 is suitable for REST API service patterns; for advanced connector logic, consider Claude 3 or Gemini 1.5.

import axios from 'axios';

const BASE_URL = '/v1/bi_connectors';

const BIConnectorsService = {
    addConnector: (payload) => axios.post(`${BASE_URL}/`, payload),
    listConnectors: () => axios.get(`${BASE_URL}/`),
    getConnector: (connectorId) => axios.get(`${BASE_URL}/${connectorId}`),
    removeConnector: (connectorId) => axios.delete(`${BASE_URL}/${connectorId}`),
    testConnection: (payload) => axios.post(`${BASE_URL}/test_connection`, payload),
};

export default BIConnectorsService;
