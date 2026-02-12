import {
    ArrowRightIcon,
    ArrowsRightLeftIcon,
    FunnelIcon,
    PlusIcon,
    XMarkIcon,
} from '@heroicons/react/24/outline';
import { useEffect, useRef, useState } from 'react';
import { useToast } from '../context/ToastContext';
import { useUser } from '../context/UserContext';
import api from '../services/api';

export default function Transfers() {
    const { user } = useUser();
    const { showToast } = useToast();
    const [transfers, setTransfers] = useState([]);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('all'); // all, sent, received
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
    }, []);

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
            const data = await api.getTransfers(100);
            const transfersList = data.recent_transfers || data;
            // Map backend fields to frontend expected format (normalize names)
            const mappedTransfers = transfersList.map(t => ({
                ...t,
                from_user_name: t.sender,
                to_user_name: t.recipient,
                from_user_id: t.sender_id || t.from_user_id || null,
                to_user_id: t.recipient_id || t.to_user_id || null,
                from_user_email: t.sender_email || t.from_user_email || null,
                to_user_email: t.recipient_email || t.to_user_email || null,
                created_at: t.timestamp || t.created_at
            }));
            setTransfers(mappedTransfers);
        } catch (err) {
            // Surface the error and avoid using demo transfers silently
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

    // Filter transfers based on selected filter
    const filteredTransfers = transfers.filter((transfer) => {
        if (filter === 'all') return true;
        if (filter === 'sent') return transfer.from_user_name === currentUserName;
        if (filter === 'received') return transfer.to_user_name === currentUserName;
        return true;
    });

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
                    <PlusIcon className="h-5 w-5 mr-2" />
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
                <div className="flex items-center space-x-4">
                    <FunnelIcon className="h-5 w-5 text-gray-400" />
                    <span className="text-sm text-gray-600 dark:text-gray-300">Filter:</span>
                    <div className="flex space-x-2">
                        {['all', 'sent', 'received'].map((f) => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
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
                                    <ArrowRightIcon className="h-4 w-4" />
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

                            {/* Details */}
                            <div className="ml-6 text-right w-48">
                                <p className="text-sm text-gray-600 dark:text-gray-300">{transfer.reason || 'No reason provided'}</p>
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
                            <XMarkIcon className="h-5 w-5" />
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
                                <ArrowsRightLeftIcon className="h-6 w-6 mr-2 text-blue-500" />
                                Reallocate Credits
                            </h2>
                            <button
                                onClick={() => setShowTransferModal(false)}
                                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                            >
                                <XMarkIcon className="h-6 w-6" />
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
