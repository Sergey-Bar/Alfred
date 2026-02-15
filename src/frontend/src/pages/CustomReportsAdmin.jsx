// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: Admin UI for custom analytics/reporting. Allows creation, scheduling, and export of custom reports (CSV/PDF/Excel). Lists all reports, supports ad-hoc run and download. Uses api.js methods for backend integration.
// Why: Enables advanced analytics, ad-hoc reporting, and scheduled exports for admins.
// Root Cause: No UI existed for custom/scheduled/exportable reports.
// Context: Use in admin dashboard. Future: add BI integration, advanced filters, and permission checks.
// Model Suitability: For React admin panels, GPT-4.1 is sufficient; for advanced analytics, consider Claude 3 or Gemini 1.5.

import { useEffect, useState } from 'react';
import api from '../services/api';

export default function CustomReportsAdmin() {
    const [reports, setReports] = useState([]);
    const [form, setForm] = useState({ name: '', description: '', query: '', schedule: '', format: 'csv', recipients: '' });
    const [message, setMessage] = useState('');
    const [running, setRunning] = useState({});

    async function fetchReports() {
        setReports(await api.listCustomReports());
    }

    useEffect(() => { fetchReports(); }, []);

    async function handleCreate(e) {
        e.preventDefault();
        await api.createCustomReport({
            ...form,
            recipients: form.recipients ? form.recipients.split(',').map(s => s.trim()) : undefined
        });
        setForm({ name: '', description: '', query: '', schedule: '', format: 'csv', recipients: '' });
        setMessage('Report created');
        fetchReports();
    }

    async function handleRun(id, format) {
        setRunning(r => ({ ...r, [id]: true }));
        const res = await api.runCustomReport(id, { format });
        setRunning(r => ({ ...r, [id]: false }));
        if (res.output_url) {
            window.open(res.output_url, '_blank');
        } else {
            setMessage('Report run failed: ' + (res.error || 'Unknown error'));
        }
    }

    return (
        <div style={{ padding: 24 }}>
            <h2>Custom Analytics & Reports</h2>
            {message && <div style={{ color: 'green', marginBottom: 8 }}>{message}</div>}
            <form onSubmit={handleCreate} style={{ marginBottom: 24 }}>
                <input required placeholder="Name" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
                <input placeholder="Description" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
                <input required placeholder="Query (SQL or DSL)" value={form.query} onChange={e => setForm(f => ({ ...f, query: e.target.value }))} />
                <input placeholder="Schedule (cron)" value={form.schedule} onChange={e => setForm(f => ({ ...f, schedule: e.target.value }))} />
                <select value={form.format} onChange={e => setForm(f => ({ ...f, format: e.target.value }))}>
                    <option value="csv">CSV</option>
                    <option value="pdf">PDF</option>
                    <option value="excel">Excel</option>
                </select>
                <input placeholder="Recipients (comma-separated emails)" value={form.recipients} onChange={e => setForm(f => ({ ...f, recipients: e.target.value }))} />
                <button type="submit">Create Report</button>
            </form>
            <h3>All Reports</h3>
            <table>
                <thead>
                    <tr><th>Name</th><th>Description</th><th>Format</th><th>Schedule</th><th>Last Run</th><th>Actions</th></tr>
                </thead>
                <tbody>
                    {reports.map(r => (
                        <tr key={r.id}>
                            <td>{r.name}</td>
                            <td>{r.description}</td>
                            <td>{r.format}</td>
                            <td>{r.schedule}</td>
                            <td>{r.last_run ? new Date(r.last_run).toLocaleString() : '-'}</td>
                            <td>
                                <button disabled={running[r.id]} onClick={() => handleRun(r.id, r.format)}>Run & Export</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
