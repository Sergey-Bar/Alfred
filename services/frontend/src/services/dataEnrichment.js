import axios from 'axios';

const API_BASE = '/api';

export const registerPipeline = async (pipeline) => {
    const res = await axios.post(`${API_BASE}/data-enrichment/pipelines`, pipeline);
    return res.data;
};

export const listPipelines = async () => {
    const res = await axios.get(`${API_BASE}/data-enrichment/pipelines`);
    return res.data;
};

export const runEnrichmentJob = async (job) => {
    const res = await axios.post(`${API_BASE}/data-enrichment/jobs`, job);
    return res.data;
};

export const listJobs = async (pipelineId) => {
    const url = pipelineId ? `${API_BASE}/data-enrichment/jobs?pipeline_id=${pipelineId}` : `${API_BASE}/data-enrichment/jobs`;
    const res = await axios.get(url);
    return res.data;
};
