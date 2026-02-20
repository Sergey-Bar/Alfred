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
