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
