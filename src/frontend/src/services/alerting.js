// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Service for Alerting & Anomaly Detection API. Methods to create, list, get, delete alert rules, trigger alerts, and fetch alert history.
// Why: Enables frontend admin UI to manage alerting and anomaly detection for analytics data.
// Root Cause: No frontend integration for new backend alerting API.
// Context: Used by admin/config UI for monitoring and automated notifications. Future: extend for real-time streaming, advanced anomaly models, and alert history/audit logging.
// Model Suitability: GPT-4.1 is suitable for REST API service patterns; for advanced anomaly detection, consider Claude 3 or Gemini 1.5.

import axios from 'axios';

const BASE_URL = '/v1/alerting';

const AlertingService = {
    createRule: (payload) => axios.post(`${BASE_URL}/rules`, payload),
    listRules: () => axios.get(`${BASE_URL}/rules`),
    getRule: (ruleId) => axios.get(`${BASE_URL}/rules/${ruleId}`),
    deleteRule: (ruleId) => axios.delete(`${BASE_URL}/rules/${ruleId}`),
    triggerAlert: (payload) => axios.post(`${BASE_URL}/trigger`, payload),
    getAlertHistory: () => axios.get(`${BASE_URL}/history`),
};

export default AlertingService;
