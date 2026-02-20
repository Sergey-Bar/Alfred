
import axios from 'axios';

const API_BASE = '/api';


// Submit a new analytics event (with error handling)
export const submitAnalyticsEvent = async (event) => {
    try {
        const res = await axios.post(`${API_BASE}/analytics/events`, event);
        return res.data;
    } catch (err) {
        // TODO: Integrate with global error handler/logging
        console.error('Failed to submit analytics event:', err);
        throw err;
    }
};


// Query analytics events by type/time (with error handling)
export const queryAnalyticsEvents = async (params = {}) => {
    const { eventType, start, end } = params;
    let url = `${API_BASE}/analytics/events`;
    const query = [];
    if (eventType) query.push(`event_type=${encodeURIComponent(eventType)}`);
    if (start) query.push(`start=${encodeURIComponent(start)}`);
    if (end) query.push(`end=${encodeURIComponent(end)}`);
    if (query.length) url += `?${query.join('&')}`;
    try {
        const res = await axios.get(url);
        return res.data;
    } catch (err) {
        // TODO: Integrate with global error handler/logging
        console.error('Failed to query analytics events:', err);
        throw err;
    }
};


// Aggregate analytics metrics (with error handling)
export const aggregateAnalytics = async (eventType) => {
    try {
        const res = await axios.get(`${API_BASE}/analytics/aggregate?event_type=${encodeURIComponent(eventType)}`);
        return res.data;
    } catch (err) {
        // TODO: Integrate with global error handler/logging
        console.error('Failed to aggregate analytics:', err);
        throw err;
    }
};

// --- FUTURE: Streaming/Real-Time Analytics (WebSockets, Kafka) ---
// export const subscribeToAnalyticsStream = (onEvent) => {
//     // TODO: Implement WebSocket/Kafka client for real-time analytics
// };

// --- FUTURE: Advanced Aggregations, BI Integration, Audit Logging, Access Controls ---
// TODO: Add methods for custom aggregations, BI/reporting tool integration, audit logging, and RBAC
