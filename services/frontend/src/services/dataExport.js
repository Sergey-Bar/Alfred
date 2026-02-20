import api from './api';

export async function exportAnalytics(format = 'csv') {
    // Fetches analytics data in the specified format (csv or json)
    const res = await api.get('/export/analytics', { params: { format } });
    return res.data;
}
