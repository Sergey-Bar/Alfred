import axios from 'axios';

const BASE_URL = '/v1/query_validation';

const QueryValidationService = {
    validateQuery: (payload) => axios.post(`${BASE_URL}/validate`, payload),
    biIntegrationCheck: (payload) => axios.post(`${BASE_URL}/bi_check`, payload),
};

export default QueryValidationService;
