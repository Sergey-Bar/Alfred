import {
    ArrowRight,
    ArrowRightLeft,
    Calendar,
    ChevronLeft,
    ChevronRight,
    Clock,
    Filter,
    Plus,
    X,
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useToast } from '../context/ToastContext';
import { useUser } from '../context/UserContext';
import api from '../services/api';

const STATUS_CONFIG = {
    pending: { label: 'Pending', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-400' },
    approved: { label: 'Approved', color: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-400' },
    rejected: { label: 'Rejected', color: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-400' },
    expired: { label: 'Expired', color: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400' },
    cancelled: { label: 'Cancelled', color: 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-500' },
};

const PAGE_SIZE = 20;

export default function Transfers() {
    const { user } = useUser();
    const { showToast } = useToast();
    const [transfers, setTransfers] = useState([]);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('all'); // all, sent, received
    const [statusFilter, setStatusFilter] = useState('all'); // all, pending, approved, rejected, expired, cancelled
    const [dateFrom, setDateFrom] = useState('');
    const [dateTo, setDateTo] = useState('');
    const [page, setPage] = useState(1);
    const [totalTransfers, setTotalTransfers] = useState(0);
    const [selectedUser, setSelectedUser] = useState(null);
    const [popoverPosition, setPopoverPosition] = useState({ top: 0, left: 0 });
    const popoverRef = useRef(null);

    // Transfer modal state
    const [showTransferModal, setShowTransferModal] = useState(false);
    const [transferForm, setTransferForm] = useState({ toUserId: '', amount: '', reason: '' });
    const [transferLoading, setTransferLoading] = useState(false);

    useEffect(() => {
        fetchTransfers();
        fetchUsers();
    }, [page]);

    async function fetchUsers() {
        try {
            const data = await api.getUsersSimple();
            setUsers(data.users || data || []);
        } catch (err) {
            // Do not silently populate demo users — surface the error instead
            setUsers([]);
            setError(err?.message || 'Failed to load users');
        }
    }

    async function handleCreateTransfer(e) {
        e.preventDefault();
        if (!transferForm.toUserId || !transferForm.amount) {
            showToast('Please select a recipient and enter an amount', 'error');
            return;
        }

        try {
            setTransferLoading(true);
            await api.createTransfer(transferForm.toUserId, parseInt(transferForm.amount), transferForm.reason);
            showToast('Transfer successful!', 'success');
            setShowTransferModal(false);
            setTransferForm({ toUserId: '', amount: '', reason: '' });
            fetchTransfers();
        } catch (err) {
            showToast(err.message || 'Transfer failed', 'error');
        } finally {
            setTransferLoading(false);
        }
    }

    async function fetchTransfers() {
        try {
            setLoading(true);
            const data = await api.getTransferHistory({ page, pageSize: PAGE_SIZE, status: statusFilter !== 'all' ? statusFilter : undefined });
            const transfersList = data.transfers || data.recent_transfers || data;
            const mappedTransfers = (Array.isArray(transfersList) ? transfersList : []).map(t => ({
                ...t,
                from_user_name: t.sender || t.from_user_name,
                to_user_name: t.recipient || t.to_user_name,
                from_user_id: t.sender_id || t.from_user_id || null,
                to_user_id: t.recipient_id || t.to_user_id || null,
                from_user_email: t.sender_email || t.from_user_email || null,
                to_user_email: t.recipient_email || t.to_user_email || null,
                created_at: t.timestamp || t.created_at,
                status: t.status || 'approved',
            }));
            setTransfers(mappedTransfers);
            setTotalTransfers(data.total ?? mappedTransfers.length);
        } catch (err) {
            setError(err?.message || 'Failed to load transfers');
            setTransfers([]);
        } finally {
            setLoading(false);
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

    // Get current user name for filtering
    const currentUserName = user?.name || '';

    // Filter transfers based on selected filters (direction + date range)
    const filteredTransfers = transfers.filter((transfer) => {
        // Direction filter
        if (filter === 'sent' && transfer.from_user_name !== currentUserName) return false;
        if (filter === 'received' && transfer.to_user_name !== currentUserName) return false;
        // Date range filter (client-side for additional precision)
        if (dateFrom && new Date(transfer.created_at) < new Date(dateFrom)) return false;
        if (dateTo && new Date(transfer.created_at) > new Date(dateTo + 'T23:59:59')) return false;
        return true;
    });

    const totalPages = Math.max(1, Math.ceil(totalTransfers / PAGE_SIZE));

    // Handle user click to show popover
    function handleUserClick(event, userName, type, transfer) {
        const rect = event.currentTarget.getBoundingClientRect();
        setPopoverPosition({
            top: rect.bottom + window.scrollY + 8,
            left: rect.left + window.scrollX,
        });
        setSelectedUser({
            name: userName,
            type,
            email: type === 'sender' ? transfer.from_user_email : transfer.to_user_email,
            userId: type === 'sender' ? transfer.from_user_id : transfer.to_user_id,
        });
    }

    // Close popover when clicking outside
    useEffect(() => {
        function handleClickOutside(event) {
            if (popoverRef.current && !popoverRef.current.contains(event.target)) {
                setSelectedUser(null);
            }
        }
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div>
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Credit Reallocation</h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-1">Manage and track credit reallocations between users</p>
                </div>
                <button
                    onClick={() => setShowTransferModal(true)}
                    className="btn btn-primary flex items-center"
                >
                    <Plus className="h-5 w-5 mr-2" />
                    Reallocate Credits
                </button>
            </div>

            {error && (
                <div className="mb-4 p-3 bg-yellow-50 text-yellow-700 rounded-lg text-sm flex items-center justify-between">
                    <div>API error: {error}. Demo data not used.</div>
                    <div className="flex items-center space-x-2">
                        <button
                            onClick={() => { setError(null); fetchTransfers(); fetchUsers(); }}
                            className="btn btn-primary"
                        >
                            Retry
                        </button>
                        <a href="mailto:support@example.com" className="btn btn-secondary">
                            Contact Support
                        </a>
                    </div>
                </div>
            )}

            {/* Filter */}
            <div className="card mb-6">
                <div className="flex flex-wrap items-center gap-4">
                    <Filter className="h-5 w-5 text-gray-400" />
                    <div>
                        <span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">Direction</span>
                        <div className="flex space-x-2">
                            {['all', 'sent', 'received'].map((f) => (
                                <button
                                    key={f}
                                    onClick={() => { setFilter(f); setPage(1); }}
                                    className={`px-3 py-1 text-sm rounded-full ${filter === f
                                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400 font-medium'
                                        : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                                        }`}
                                >
                                    {f.charAt(0).toUpperCase() + f.slice(1)}
                                </button>
                            ))}
                        </div>
                    </div>
                    <div className="border-l border-gray-200 dark:border-gray-600 pl-4">
                        <span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">Status</span>
                        <div className="flex space-x-2">
                            {['all', 'pending', 'approved', 'rejected', 'expired'].map((s) => (
                                <button
                                    key={s}
                                    onClick={() => { setStatusFilter(s); setPage(1); fetchTransfers(); }}
                                    className={`px-3 py-1 text-sm rounded-full ${statusFilter === s
                                        ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400 font-medium'
                                        : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                                        }`}
                                >
                                    {s.charAt(0).toUpperCase() + s.slice(1)}
                                </button>
                            ))}
                        </div>
                    </div>
                    <div className="border-l border-gray-200 dark:border-gray-600 pl-4">
                        <span className="text-xs text-gray-500 dark:text-gray-400 block mb-1">Date Range</span>
                        <div className="flex items-center gap-2">
                            <div className="relative">
                                <Calendar className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                                <input
                                    type="date"
                                    value={dateFrom}
                                    onChange={(e) => { setDateFrom(e.target.value); setPage(1); }}
                                    className="input pl-8 py-1 text-sm w-36"
                                    placeholder="From"
                                />
                            </div>
                            <span className="text-gray-400 text-sm">to</span>
                            <div className="relative">
                                <Calendar className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                                <input
                                    type="date"
                                    value={dateTo}
                                    onChange={(e) => { setDateTo(e.target.value); setPage(1); }}
                                    className="input pl-8 py-1 text-sm w-36"
                                    placeholder="To"
                                />
                            </div>
                            {(dateFrom || dateTo) && (
                                <button
                                    onClick={() => { setDateFrom(''); setDateTo(''); setPage(1); }}
                                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                                >
                                    <X className="h-4 w-4" />
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="stat-card">
                    <p className="stat-value">{filteredTransfers.length}</p>
                    <p className="stat-label">{filter === 'all' ? 'Total' : filter === 'sent' ? 'Sent' : 'Received'} Transfers</p>
                </div>
                <div className="stat-card">
                    <p className="stat-value">
                        {filteredTransfers.reduce((sum, t) => sum + (t.amount || 0), 0).toLocaleString()}
                    </p>
                    <p className="stat-label">Total Credits {filter === 'sent' ? 'Sent' : filter === 'received' ? 'Received' : 'Reallocated'}</p>
                </div>
                <div className="stat-card">
                    <p className="stat-value">
                        {filteredTransfers.length > 0
                            ? Math.round(filteredTransfers.reduce((sum, t) => sum + (t.amount || 0), 0) / filteredTransfers.length).toLocaleString()
                            : 0}
                    </p>
                    <p className="stat-label">Average Reallocation</p>
                </div>
            </div>

            {/* Transfers List */}
            <div className="card relative">
                <div className="space-y-4">
                    {filteredTransfers.map((transfer) => (
                        <div
                            key={transfer.id}
                            className="flex items-center p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        >
                            {/* From User */}
                            <div className="flex-1">
                                <button
                                    onClick={(e) => handleUserClick(e, transfer.from_user_name, 'sender', transfer)}
                                    className="font-medium text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 cursor-pointer transition-colors text-left"
                                >
                                    {transfer.from_user_name}
                                </button>
                                <p className="text-sm text-gray-500 dark:text-gray-400">Sender</p>
                            </div>

                            {/* Arrow and Amount */}
                            <div className="flex items-center px-6">
                                <div className="flex items-center bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-400 px-4 py-2 rounded-full">
                                    <span className="font-semibold mr-2">{transfer.amount?.toLocaleString()}</span>
                                    <ArrowRight className="h-4 w-4" />
                                </div>
                            </div>

                            {/* To User */}
                            <div className="flex-1 text-right">
                                <button
                                    onClick={(e) => handleUserClick(e, transfer.to_user_name, 'recipient', transfer)}
                                    className="font-medium text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 cursor-pointer transition-colors text-right"
                                >
                                    {transfer.to_user_name}
                                </button>
                                <p className="text-sm text-gray-500 dark:text-gray-400">Recipient</p>
                            </div>

                            {/* Details + Status */}
                            <div className="ml-6 text-right w-56">
                                <div className="flex items-center justify-end gap-2 mb-1">
                                    {transfer.status && STATUS_CONFIG[transfer.status] && (
                                        <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full ${STATUS_CONFIG[transfer.status].color}`}>
                                            {transfer.status === 'pending' && <Clock className="h-3 w-3 mr-1" />}
                                            {STATUS_CONFIG[transfer.status].label}
                                        </span>
                                    )}
                                </div>
                                <p className="text-sm text-gray-600 dark:text-gray-300 truncate">{transfer.reason || 'No reason provided'}</p>
                                <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">{formatDate(transfer.created_at)}</p>
                            </div>
                        </div>
                    ))}

                    {filteredTransfers.length === 0 && (
                        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                            {filter === 'all' ? 'No reallocations found' : `No ${filter} reallocations found`}
                        </div>
                    )}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                    <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                            Showing {Math.min((page - 1) * PAGE_SIZE + 1, totalTransfers)}–{Math.min(page * PAGE_SIZE, totalTransfers)} of {totalTransfers} transfers
                        </p>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                                className="btn btn-secondary flex items-center px-3 py-1.5 text-sm disabled:opacity-40"
                            >
                                <ChevronLeft className="h-4 w-4 mr-1" /> Prev
                            </button>
                            <span className="text-sm text-gray-600 dark:text-gray-300 px-2">
                                Page {page} of {totalPages}
                            </span>
                            <button
                                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                disabled={page === totalPages}
                                className="btn btn-secondary flex items-center px-3 py-1.5 text-sm disabled:opacity-40"
                            >
                                Next <ChevronRight className="h-4 w-4 ml-1" />
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* User Info Popover */}
            {selectedUser && (
                <div
                    ref={popoverRef}
                    className="fixed z-50 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-4 min-w-64"
                    style={{ top: popoverPosition.top, left: popoverPosition.left }}
                >
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                            {selectedUser.type === 'sender' ? 'Sender' : 'Recipient'} Info
                        </h3>
                        <button
                            onClick={() => setSelectedUser(null)}
                            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                        >
                            <X className="h-5 w-5" />
                        </button>
                    </div>
                    <div className="space-y-2">
                        <div>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Name</p>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">{selectedUser.name}</p>
                        </div>
                        {selectedUser.email && (
                            <div>
                                <p className="text-xs text-gray-500 dark:text-gray-400">Email</p>
                                <p className="text-sm text-gray-700 dark:text-gray-300">{selectedUser.email}</p>
                            </div>
                        )}
                        {selectedUser.userId && (
                            <div>
                                <p className="text-xs text-gray-500 dark:text-gray-400">User ID</p>
                                <p className="text-sm text-gray-700 dark:text-gray-300 font-mono">{selectedUser.userId}</p>
                            </div>
                        )}
                        {!selectedUser.email && !selectedUser.userId && (
                            <p className="text-sm text-gray-500 dark:text-gray-400 italic">No additional info available</p>
                        )}
                    </div>
                </div>
            )}

            {/* Transfer Modal */}
            {showTransferModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md p-6">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center">
                                <ArrowRightLeft className="h-6 w-6 mr-2 text-blue-500" />
                                Reallocate Credits
                            </h2>
                            <button
                                onClick={() => setShowTransferModal(false)}
                                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                            >
                                <X className="h-6 w-6" />
                            </button>
                        </div>
                        <form onSubmit={handleCreateTransfer} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Recipient
                                </label>
                                <select
                                    value={transferForm.toUserId}
                                    onChange={(e) => setTransferForm({ ...transferForm, toUserId: e.target.value })}
                                    className="input w-full"
                                    required
                                >
                                    <option value="">Select a user...</option>
                                    {users.filter(u => u.user_id !== user?.id).map((u) => (
                                        <option key={u.user_id} value={u.user_id}>
                                            {u.name} ({u.email})
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Amount (credits)
                                </label>
                                <input
                                    type="number"
                                    min="1"
                                    value={transferForm.amount}
                                    onChange={(e) => setTransferForm({ ...transferForm, amount: e.target.value })}
                                    className="input w-full"
                                    placeholder="Enter credit amount"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Reason (optional)
                                </label>
                                <textarea
                                    value={transferForm.reason}
                                    onChange={(e) => setTransferForm({ ...transferForm, reason: e.target.value })}
                                    className="input w-full"
                                    rows={3}
                                    placeholder="Business justification for this reallocation"
                                />
                            </div>
                            <div className="flex justify-end space-x-3 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowTransferModal(false)}
                                    className="btn btn-secondary"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                    disabled={transferLoading}
                                >
                                    {transferLoading ? 'Processing...' : 'Reallocate Credits'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
