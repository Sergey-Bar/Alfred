import api from './api';

export async function fetchUsageAnalytics(period = '7d') {
    if (!['7d', '30d', '90d'].includes(period)) {
        throw new Error('Invalid period specified. Allowed values are: 7d, 30d, 90d.');
    }

    try {
        const res = await api.get('/analytics/usage', { params: { period } });
        return res.data;
    } catch (error) {
        console.error('Error fetching usage analytics:', error);
        throw new Error('Failed to fetch usage analytics. Please try again later.');
    }
}
