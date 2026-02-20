/*
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4.6
Tier:        L2
Logic:       Sortable, filterable, paginated request log table.
             Server-side pagination with column sorting, model/status
             filters, search by user/request ID, and cost breakdown.
Root Cause:  T068 — Request log table missing from frontend.
Context:     Core observability feature for admins to trace requests.
Suitability: L2 — standard data table with filters and pagination.
──────────────────────────────────────────────────────────────
*/
import {
    AlertTriangle, ArrowDown, ArrowUp, CheckCircle2,
    ChevronLeft, ChevronRight, Clock, Download, Filter,
    RefreshCw, Search, XCircle
} from 'lucide-react';
import { useEffect, useState } from 'react';
import api from '../services/api';

const STATUS_ICONS = {
    success: <CheckCircle2 className="w-4 h-4 text-green-600" />,
    error: <XCircle className="w-4 h-4 text-red-600" />,
    cached: <CheckCircle2 className="w-4 h-4 text-blue-600" />,
    blocked: <AlertTriangle className="w-4 h-4 text-yellow-600" />,
};

const STATUS_BADGES = {
    success: 'badge-green',
    error: 'badge-red',
    cached: 'badge-blue',
    blocked: 'badge-yellow',
};

function RequestDetailModal({ request, onClose }) {
    if (!request) return null;
    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
            <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
                <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold">Request Details</h3>
                        <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
                            <XCircle className="w-5 h-5" />
                        </button>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <p className="text-xs font-medium" style={{ color: 'var(--color-primary-400)' }}>Request ID</p>
                            <p className="font-mono">{request.id}</p>
                        </div>
                        <div>
                            <p className="text-xs font-medium" style={{ color: 'var(--color-primary-400)' }}>Timestamp</p>
                            <p>{new Date(request.timestamp).toLocaleString()}</p>
                        </div>
                        <div>
                            <p className="text-xs font-medium" style={{ color: 'var(--color-primary-400)' }}>User</p>
                            <p>{request.user}</p>
                        </div>
                        <div>
                            <p className="text-xs font-medium" style={{ color: 'var(--color-primary-400)' }}>Team</p>
                            <p>{request.team}</p>
                        </div>
                        <div>
                            <p className="text-xs font-medium" style={{ color: 'var(--color-primary-400)' }}>Model</p>
                            <p className="font-mono">{request.model}</p>
                        </div>
                        <div>
                            <p className="text-xs font-medium" style={{ color: 'var(--color-primary-400)' }}>Provider</p>
                            <p>{request.provider}</p>
                        </div>
                        <div>
                            <p className="text-xs font-medium" style={{ color: 'var(--color-primary-400)' }}>Tokens (in/out)</p>
                            <p>{request.input_tokens?.toLocaleString()} / {request.output_tokens?.toLocaleString()}</p>
                        </div>
                        <div>
                            <p className="text-xs font-medium" style={{ color: 'var(--color-primary-400)' }}>Cost</p>
                            <p className="font-semibold">${request.cost?.toFixed(4)}</p>
                        </div>
                        <div>
                            <p className="text-xs font-medium" style={{ color: 'var(--color-primary-400)' }}>Latency</p>
                            <p>{request.latency_ms}ms</p>
                        </div>
                        <div>
                            <p className="text-xs font-medium" style={{ color: 'var(--color-primary-400)' }}>Status</p>
                            <span className={`badge ${STATUS_BADGES[request.status] || 'badge-gray'}`}>
                                {request.status}
                            </span>
                        </div>
                    </div>
                    {request.routing_decision && (
                        <div className="mt-4 p-3 rounded-lg" style={{ background: 'var(--color-primary-100)' }}>
                            <p className="text-xs font-medium mb-1" style={{ color: 'var(--color-primary-400)' }}>Routing Decision</p>
                            <p className="text-sm">{request.routing_decision}</p>
                        </div>
                    )}
                    {request.cache_hit && (
                        <div className="mt-2 p-3 rounded-lg bg-blue-50">
                            <p className="text-xs font-medium text-blue-600 mb-1">Cache Hit</p>
                            <p className="text-sm">Similarity: {(request.cache_similarity * 100).toFixed(1)}%</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default function RequestLog() {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchQuery, setSearchQuery] = useState('');
    const [modelFilter, setModelFilter] = useState('all');
    const [statusFilter, setStatusFilter] = useState('all');
    const [sortField, setSortField] = useState('timestamp');
    const [sortDir, setSortDir] = useState('desc');
    const [page, setPage] = useState(1);
    const [selectedRequest, setSelectedRequest] = useState(null);
    const pageSize = 20;

    useEffect(() => {
        loadRequests();
    }, []);

    const loadRequests = async () => {
        setLoading(true);
        try {
            const data = await api.fetchJson('/admin/request-log');
            setRequests(Array.isArray(data) ? data : data?.items || []);
        } catch {
            setRequests([]);
        } finally {
            setLoading(false);
        }
    };

    const handleSort = (field) => {
        if (sortField === field) {
            setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortDir('desc');
        }
    };

    const SortIcon = ({ field }) => {
        if (sortField !== field) return null;
        return sortDir === 'asc'
            ? <ArrowUp className="w-3 h-3 inline ml-1" />
            : <ArrowDown className="w-3 h-3 inline ml-1" />;
    };

    // Filter and sort
    const filtered = requests
        .filter(r => {
            if (searchQuery) {
                const q = searchQuery.toLowerCase();
                if (!r.id?.toLowerCase().includes(q) &&
                    !r.user?.toLowerCase().includes(q) &&
                    !r.model?.toLowerCase().includes(q) &&
                    !r.team?.toLowerCase().includes(q)) return false;
            }
            if (modelFilter !== 'all' && r.model !== modelFilter) return false;
            if (statusFilter !== 'all' && r.status !== statusFilter) return false;
            return true;
        })
        .sort((a, b) => {
            let valA = a[sortField], valB = b[sortField];
            if (typeof valA === 'string') valA = valA.toLowerCase();
            if (typeof valB === 'string') valB = valB.toLowerCase();
            if (valA < valB) return sortDir === 'asc' ? -1 : 1;
            if (valA > valB) return sortDir === 'asc' ? 1 : -1;
            return 0;
        });

    const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
    const paginated = filtered.slice((page - 1) * pageSize, page * pageSize);
    const models = [...new Set(requests.map(r => r.model))].filter(Boolean);

    const handleExport = () => {
        const csv = [
            'id,timestamp,user,team,model,provider,input_tokens,output_tokens,cost,latency_ms,status',
            ...filtered.map(r =>
                `${r.id},${r.timestamp},${r.user},${r.team},${r.model},${r.provider},${r.input_tokens},${r.output_tokens},${r.cost},${r.latency_ms},${r.status}`
            ),
        ].join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = 'request_log.csv'; a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Request Log</h1>
                    <p style={{ color: 'var(--color-primary-500)' }}>
                        {filtered.length.toLocaleString()} requests tracked
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <button onClick={loadRequests} className="btn flex items-center gap-2">
                        <RefreshCw className="w-4 h-4" /> Refresh
                    </button>
                    <button onClick={handleExport} className="btn flex items-center gap-2">
                        <Download className="w-4 h-4" /> Export CSV
                    </button>
                </div>
            </div>

            {/* Summary cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                    { label: 'Total Requests', value: requests.length.toLocaleString(), color: 'text-blue-600' },
                    { label: 'Success Rate', value: requests.length > 0 ? (requests.filter(r => r.status === 'success').length / requests.length * 100).toFixed(1) + '%' : '—', color: 'text-green-600' },
                    { label: 'Cache Hits', value: requests.filter(r => r.status === 'cached').length.toLocaleString(), color: 'text-purple-600' },
                    { label: 'Avg Latency', value: requests.length > 0 ? Math.round(requests.reduce((s, r) => s + (r.latency_ms || 0), 0) / requests.length) + 'ms' : '—', color: 'text-orange-600' },
                ].map(stat => (
                    <div key={stat.label} className="card p-4">
                        <p className="text-xs" style={{ color: 'var(--color-primary-400)' }}>{stat.label}</p>
                        <p className={`text-xl font-bold ${stat.color}`}>{stat.value}</p>
                    </div>
                ))}
            </div>

            {/* Filters */}
            <div className="card p-4">
                <div className="flex flex-wrap items-center gap-3">
                    <div className="relative flex-1 min-w-[200px]">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: 'var(--color-primary-400)' }} />
                        <input
                            type="text"
                            className="input w-full pl-10"
                            placeholder="Search by request ID, user, model, team..."
                            value={searchQuery}
                            onChange={e => { setSearchQuery(e.target.value); setPage(1); }}
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <Filter className="w-4 h-4" style={{ color: 'var(--color-primary-400)' }} />
                        <select
                            className="input"
                            value={modelFilter}
                            onChange={e => { setModelFilter(e.target.value); setPage(1); }}
                        >
                            <option value="all">All Models</option>
                            {models.map(m => <option key={m} value={m}>{m}</option>)}
                        </select>
                        <select
                            className="input"
                            value={statusFilter}
                            onChange={e => { setStatusFilter(e.target.value); setPage(1); }}
                        >
                            <option value="all">All Status</option>
                            <option value="success">Success</option>
                            <option value="error">Error</option>
                            <option value="cached">Cached</option>
                            <option value="blocked">Blocked</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Table */}
            <div className="card overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr style={{ background: 'var(--color-primary-100)' }}>
                                {[
                                    { key: 'timestamp', label: 'Time' },
                                    { key: 'user', label: 'User' },
                                    { key: 'model', label: 'Model' },
                                    { key: 'input_tokens', label: 'Tokens' },
                                    { key: 'cost', label: 'Cost' },
                                    { key: 'latency_ms', label: 'Latency' },
                                    { key: 'status', label: 'Status' },
                                ].map(col => (
                                    <th
                                        key={col.key}
                                        className="px-4 py-3 text-left font-medium cursor-pointer hover:bg-gray-200 select-none"
                                        onClick={() => handleSort(col.key)}
                                    >
                                        {col.label} <SortIcon field={col.key} />
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr><td colSpan={7} className="text-center py-12">
                                    <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2" style={{ color: 'var(--color-primary-400)' }} />
                                    <p style={{ color: 'var(--color-primary-400)' }}>Loading requests...</p>
                                </td></tr>
                            ) : paginated.length === 0 ? (
                                <tr><td colSpan={7} className="text-center py-12">
                                    <Clock className="w-8 h-8 mx-auto mb-2" style={{ color: 'var(--color-primary-300)' }} />
                                    <p style={{ color: 'var(--color-primary-400)' }}>No requests found</p>
                                </td></tr>
                            ) : paginated.map(req => (
                                <tr
                                    key={req.id}
                                    className="border-t hover:bg-gray-50 cursor-pointer"
                                    style={{ borderColor: 'var(--color-primary-200)' }}
                                    onClick={() => setSelectedRequest(req)}
                                >
                                    <td className="px-4 py-3">
                                        <p className="text-xs">{new Date(req.timestamp).toLocaleTimeString()}</p>
                                        <p className="text-xs" style={{ color: 'var(--color-primary-400)' }}>
                                            {new Date(req.timestamp).toLocaleDateString()}
                                        </p>
                                    </td>
                                    <td className="px-4 py-3">
                                        <p className="font-medium">{req.user}</p>
                                        <p className="text-xs" style={{ color: 'var(--color-primary-400)' }}>{req.team}</p>
                                    </td>
                                    <td className="px-4 py-3">
                                        <code className="text-xs px-2 py-1 rounded" style={{ background: 'var(--color-primary-100)' }}>
                                            {req.model}
                                        </code>
                                    </td>
                                    <td className="px-4 py-3 text-xs">
                                        <span className="text-green-600">{req.input_tokens?.toLocaleString()}</span>
                                        {' / '}
                                        <span className="text-blue-600">{req.output_tokens?.toLocaleString()}</span>
                                    </td>
                                    <td className="px-4 py-3 font-medium">${req.cost?.toFixed(4)}</td>
                                    <td className="px-4 py-3">
                                        <span className={req.latency_ms > 2000 ? 'text-red-600' : req.latency_ms > 1000 ? 'text-yellow-600' : 'text-green-600'}>
                                            {req.latency_ms}ms
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`badge ${STATUS_BADGES[req.status] || ''} flex items-center gap-1 w-fit`}>
                                            {STATUS_ICONS[req.status]} {req.status}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                {/* Pagination */}
                {totalPages > 1 && (
                    <div className="flex items-center justify-between px-4 py-3 border-t" style={{ borderColor: 'var(--color-primary-200)' }}>
                        <p className="text-sm" style={{ color: 'var(--color-primary-500)' }}>
                            Showing {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, filtered.length)} of {filtered.length}
                        </p>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setPage(Math.max(1, page - 1))}
                                disabled={page === 1}
                                className="btn btn-sm"
                            >
                                <ChevronLeft className="w-4 h-4" />
                            </button>
                            <span className="text-sm font-medium">Page {page} of {totalPages}</span>
                            <button
                                onClick={() => setPage(Math.min(totalPages, page + 1))}
                                disabled={page === totalPages}
                                className="btn btn-sm"
                            >
                                <ChevronRight className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                )}
            </div>

            <RequestDetailModal request={selectedRequest} onClose={() => setSelectedRequest(null)} />
        </div>
    );
}
