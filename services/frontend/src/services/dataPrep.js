import axios from 'axios';

const BASE_URL = '/v1/data_prep';

const DataPrepService = {
    createJob: (payload) => axios.post(`${BASE_URL}/jobs`, payload),
    listJobs: () => axios.get(`${BASE_URL}/jobs`),
    getJob: (jobId) => axios.get(`${BASE_URL}/jobs/${jobId}`),
    deleteJob: (jobId) => axios.delete(`${BASE_URL}/jobs/${jobId}`),
    previewTransformation: (payload) => axios.post(`${BASE_URL}/preview`, payload),
};

export default DataPrepService;
