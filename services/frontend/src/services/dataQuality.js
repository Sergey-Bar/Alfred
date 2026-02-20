import axios from 'axios';

const API_BASE = '/api';

export const reportDataQualityEvent = async (event) => {
    try {
        const res = await axios.post(`${API_BASE}/data-quality/events`, event);
        return res.data;
    } catch (error) {
        console.error('Error reporting data quality event:', error);
        throw new Error('Failed to report data quality event. Please try again later.');
    }
};

export const getDataQualityEvents = async (dataset) => {
    if (dataset && typeof dataset !== 'string') {
        throw new Error('Invalid dataset parameter. It must be a string.');
    }

    try {
        const url = dataset ? `${API_BASE}/data-quality/events?dataset=${encodeURIComponent(dataset)}` : `${API_BASE}/data-quality/events`;
        const res = await axios.get(url);
        return res.data;
    } catch (error) {
        console.error('Error fetching data quality events:', error);
        throw new Error('Failed to fetch data quality events. Please try again later.');
    }
};

export const getHighSeverityAlerts = async () => {
    try {
        const res = await axios.get(`${API_BASE}/data-quality/alerts`);
        return res.data;
    } catch (error) {
        console.error('Error fetching high severity alerts:', error);
        throw new Error('Failed to fetch high severity alerts. Please try again later.');
    }
};
