import {
    CheckCircle2,
    Clock,
    FileText,
    Plus,
    XCircle,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import Modal from '../components/Modal';
import { useToast } from '../context/ToastContext';

import api from '../services/api';

export default function Approvals() {

    const { showToast } = useToast();
    const [approvals, setApprovals] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('pending'); // pending, approved, rejected, all
    const [showRequestModal, setShowRequestModal] = useState(false);
    const [requestForm, setRequestForm] = useState({ amount: '', reason: '' });
    const [requestLoading, setRequestLoading] = useState(false);
    const [actionLoading, setActionLoading] = useState(null);

    useEffect(() => {
        fetchApprovals();
    }, []);

    async function fetchApprovals() {
        try {
            setLoading(true);
            const data = await api.getPendingApprovals();
            // Map consistent fields
            const rawData = Array.isArray(data) ? data : (data.approvals || []);
            const approvalsList = rawData.map(a => ({
                ...a,
                user_name: a.user_name || 'Unknown User',
                user_email: a.user_email || '',
                requested_amount: a.requested_credits || a.requested_amount, // fallback for UI compat
                approved_amount: a.approved_credits || a.approved_amount     // fallback for UI compat
            }));
            setApprovals(approvalsList);
        } catch (err) {
            // Surface error; do not fall back to demo data silently
            setError(err?.message || 'Failed to load approvals');
            setApprovals([]);
        } finally {
            setLoading(false);
        }
    }

    async function handleCreateRequest(e) {
        e.preventDefault();
        if (!requestForm.amount || !requestForm.reason) {
            showToast('Please enter amount and reason', 'error');
            return;
        }

        try {
            setRequestLoading(true);
            await api.createApprovalRequest(parseInt(requestForm.amount), requestForm.reason);
            showToast('Quota request submitted successfully', 'success');
            setShowRequestModal(false);
            setRequestForm({ amount: '', reason: '' });
            fetchApprovals();
        } catch (err) {
            showToast(err.message || 'Failed to submit request', 'error');
        } finally {
            setRequestLoading(false);
        }
    }

    async function handleApprove(approvalId, approvedAmount = null) {
        try {
            setActionLoading(approvalId);
            await api.approveRequest(approvalId, approvedAmount);
            showToast('Request approved', 'success');
            fetchApprovals();
        } catch (err) {
            showToast(err.message || 'Failed to approve request', 'error');
        } finally {
            setActionLoading(null);
        }
    }

    async function handleReject(approvalId) {
        const reason = prompt('Reason for rejection (optional):');
        try {
            setActionLoading(approvalId);
            await api.rejectRequest(approvalId, reason || '');
            showToast('Request rejected', 'success');
            fetchApprovals();
        } catch (err) {
            showToast(err.message || 'Failed to reject request', 'error');
        } finally {
            setActionLoading(null);
        }
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    }

    const filteredApprovals = approvals.filter((a) => {
        if (filter === 'all') return true;
        return a.status === filter;
    });

    const stats = {
        pending: approvals.filter(a => a.status === 'pending').length,
        approved: approvals.filter(a => a.status === 'approved').length,
        rejected: approvals.filter(a => a.status === 'rejected').length,
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div>
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Quota Approvals</h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-1">Manage quota increase requests</p>
                </div>
                <button
                    onClick={() => setShowRequestModal(true)}
                    className="btn btn-primary flex items-center"
                >
                    <Plus className="h-5 w-5 mr-2" />
                    Request Quota
                </button>
            </div>

            {error && (
                <div className="mb-4 p-3 bg-yellow-900/30 text-yellow-400 rounded-lg text-sm flex items-center justify-between">
                    <div>API error: {error}. Demo data not used.</div>
                    <div className="flex items-center space-x-2">
                        <button onClick={() => { setError(null); fetchApprovals(); }} className="btn btn-primary">Retry</button>
                        <a href="mailto:support@example.com" className="btn btn-secondary">Contact Support</a>
                    </div>
                </div>
            )}

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="stat-card">
                    <div className="flex items-center">
                        <Clock className="h-8 w-8 text-yellow-500 mr-3" />
                        <div>
                            <p className="stat-value">{stats.pending}</p>
                            <p className="stat-label">Pending</p>
                        </div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="flex items-center">
                        <CheckCircle2 className="h-8 w-8 text-green-500 mr-3" />
                        <div>
                            <p className="stat-value">{stats.approved}</p>
                            <p className="stat-label">Approved</p>
                        </div>
                    </div>
                </div>
                <div className="stat-card">
                    <div className="flex items-center">
                        <XCircle className="h-8 w-8 text-red-500 mr-3" />
                        <div>
                            <p className="stat-value">{stats.rejected}</p>
                            <p className="stat-label">Rejected</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Filter */}
            <div className="card mb-6">
                <div className="flex space-x-2">
                    {['pending', 'approved', 'rejected', 'all'].map((f) => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-4 py-2 text-sm rounded-lg ${filter === f
                                ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400 font-medium'
                                : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                                }`}
                        >
                            {f.charAt(0).toUpperCase() + f.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            {/* Approvals List */}
            <div className="card">
                <div className="space-y-4">
                    {filteredApprovals.map((approval) => (
                        <div
                            key={approval.id}
                            className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <div className="flex items-center mb-2">
                                        <h3 className="font-semibold text-gray-900 dark:text-white mr-3">
                                            {approval.user_name}
                                        </h3>
                                        <span className={`badge ${approval.status === 'pending' ? 'badge-yellow' :
                                            approval.status === 'approved' ? 'badge-green' :
                                                'badge-red'
                                            }`}>
                                            {approval.status}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                                        {approval.user_email}
                                    </p>
                                    <div className="flex items-center text-sm mb-2">
                                        <FileText className="h-4 w-4 text-gray-400 mr-2" />
                                        <span className="text-gray-600 dark:text-gray-300">{approval.reason}</span>
                                    </div>
                                    <p className="text-xs text-gray-400">{formatDate(approval.created_at)}</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-lg font-bold text-gray-900 dark:text-white mb-2">
                                        {(approval.requested_credits || approval.requested_amount)?.toLocaleString()} tokens
                                    </p>
                                    {approval.status === 'approved' && (approval.approved_credits || approval.approved_amount) && (
                                        <p className="text-sm text-green-500">
                                            Approved: {(approval.approved_credits || approval.approved_amount).toLocaleString()}
                                        </p>
                                    )}
                                    {approval.status === 'rejected' && approval.rejection_reason && (
                                        <p className="text-sm text-red-400">
                                            {approval.rejection_reason}
                                        </p>
                                    )}
                                    {approval.status === 'pending' && (
                                        <div className="flex space-x-2 mt-2">
                                            <button
                                                onClick={() => handleApprove(approval.id, approval.requested_credits || approval.requested_amount)}
                                                disabled={actionLoading === approval.id}
                                                className="btn btn-sm bg-green-600 hover:bg-green-700 text-white"
                                            >
                                                <CheckCircle2 className="h-4 w-4 mr-1" />
                                                Approve
                                            </button>
                                            <button
                                                onClick={() => handleReject(approval.id)}
                                                disabled={actionLoading === approval.id}
                                                className="btn btn-sm bg-red-600 hover:bg-red-700 text-white"
                                            >
                                                <XCircle className="h-4 w-4 mr-1" />
                                                Reject
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}

                    {filteredApprovals.length === 0 && (
                        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                            No {filter === 'all' ? '' : filter} requests found
                        </div>
                    )}
                </div>
            </div>

            {/* Request Modal - Accessible with focus trapping */}
            <Modal
                isOpen={showRequestModal}
                onClose={() => setShowRequestModal(false)}
                title="Request Additional Quota"
            >
                <form onSubmit={handleCreateRequest} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Amount Requested (tokens)
                        </label>
                        <input
                            type="number"
                            min="1"
                            value={requestForm.amount}
                            onChange={(e) => setRequestForm({ ...requestForm, amount: e.target.value })}
                            className="input w-full"
                            placeholder="e.g., 5000"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Reason / Justification
                        </label>
                        <textarea
                            value={requestForm.reason}
                            onChange={(e) => setRequestForm({ ...requestForm, reason: e.target.value })}
                            className="input w-full"
                            rows={4}
                            placeholder="Explain why you need additional tokens..."
                            required
                        />
                    </div>
                    <div className="flex justify-end space-x-3 pt-4">
                        <button
                            type="button"
                            onClick={() => setShowRequestModal(false)}
                            className="btn btn-secondary"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="btn btn-primary"
                            disabled={requestLoading}
                        >
                            {requestLoading ? 'Submitting...' : 'Submit Request'}
                        </button>
                    </div>
                </form>
            </Modal>
        </div>
    );
}
