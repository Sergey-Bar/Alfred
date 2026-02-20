import api from './api';

export async function fetchKpis(page = 1, pageSize = 10) {
    // Fetches predefined KPIs from the backend
    try {
        const res = await api.get('/metrics/kpis', { params: { page, pageSize } });
        return res.data;
    } catch (error) {
        console.error('Error fetching KPIs:', error);
        throw new Error('Failed to fetch KPIs. Please try again later.');
    }
}
