// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Service for Data Preparation & Transformation API. Methods to create, list, get, delete jobs, and preview transformations for no-code/low-code data prep.
// Why: Enables frontend admin/user UI to manage and preview data prep/transformation jobs.
// Root Cause: No frontend integration for new backend data prep API.
// Context: Used by admin/user UI for data cleaning, transformation, and enrichment. Future: extend for workflow chaining, scheduling, and audit logging.
// Model Suitability: GPT-4.1 is suitable for REST API service patterns; for advanced workflow logic, consider Claude 3 or Gemini 1.5.

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
