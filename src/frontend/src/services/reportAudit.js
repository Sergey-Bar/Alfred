// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Service for Audit Logging & Permission Checks API. Methods to log/report access, fetch audit logs, and check/report permissions for report actions.
// Why: Enables frontend admin/report UI to manage audit logging and permission checks for reports.
// Root Cause: No frontend integration for new backend audit/permission API.
// Context: Used by admin/report UI for compliance, traceability, and secure access. Future: extend for persistent logs, advanced permission engines, and alerting.
// Model Suitability: GPT-4.1 is suitable for REST API service patterns; for advanced compliance, consider Claude 3 or Gemini 1.5.

import axios from 'axios';

const BASE_URL = '/v1/report_audit';

const ReportAuditService = {
    logAccess: (payload) => axios.post(`${BASE_URL}/log_access`, payload),
    getAuditLogs: () => axios.get(`${BASE_URL}/logs`),
    checkPermission: (payload) => axios.post(`${BASE_URL}/check_permission`, payload),
};

export default ReportAuditService;
