// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Scaffold a frontend service for Data Enrichment Pipelines API endpoints.
// Why: Enables the React dashboard to register, run, and monitor enrichment pipelines and jobs.
// Root Cause: No frontend integration existed for the new backend API.
// Context: This service provides methods for registering pipelines, listing pipelines, running jobs, and listing jobs. Future: add error handling, persistent storage, and scheduling. For advanced enrichment orchestration, consider using a more advanced model (Claude Opus).

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
