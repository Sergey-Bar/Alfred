import axios from 'axios';

const BASE_URL = '/v1/sharing';

const SharingService = {
    createShareLink: (payload) => axios.post(`${BASE_URL}/links`, payload),
    listShareLinks: () => axios.get(`${BASE_URL}/links`),
    getShareLink: (linkId) => axios.get(`${BASE_URL}/links/${linkId}`),
    revokeShareLink: (linkId) => axios.delete(`${BASE_URL}/links/${linkId}`),
};

export default SharingService;
