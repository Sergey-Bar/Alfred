import axios from 'axios';

const BASE_URL = '/v1/report_audit';

const ReportAuditService = {
    logAccess: (payload) => axios.post(`${BASE_URL}/log_access`, payload),
    getAuditLogs: () => axios.get(`${BASE_URL}/logs`),
    checkPermission: (payload) => axios.post(`${BASE_URL}/check_permission`, payload),
};

export default ReportAuditService;
