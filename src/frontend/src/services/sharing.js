// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Service for Collaboration & Sharing API. Methods to create, list, get, revoke share links for dashboards/reports.
// Why: Enables frontend admin/user UI to manage secure sharing of analytics assets.
// Root Cause: No frontend integration for new backend sharing API.
// Context: Used by admin/user UI for collaboration and sharing. Future: extend for audit logging, external sharing, and advanced permissions.
// Model Suitability: GPT-4.1 is suitable for REST API service patterns; for advanced sharing logic, consider Claude 3 or Gemini 1.5.

import axios from 'axios';

const BASE_URL = '/v1/sharing';

const SharingService = {
    createShareLink: (payload) => axios.post(`${BASE_URL}/links`, payload),
    listShareLinks: () => axios.get(`${BASE_URL}/links`),
    getShareLink: (linkId) => axios.get(`${BASE_URL}/links/${linkId}`),
    revokeShareLink: (linkId) => axios.delete(`${BASE_URL}/links/${linkId}`),
};

export default SharingService;
