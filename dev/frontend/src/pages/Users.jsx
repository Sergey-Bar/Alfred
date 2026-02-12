import {
    MagnifyingGlassIcon,
    PencilIcon,
    PlusIcon,
    TrashIcon,
} from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';
import DeleteConfirmDialog from '../components/DeleteConfirmDialog';
import { useToast } from '../context/ToastContext';
import api from '../services/api';

export default function Users() {
    const { showToast } = useToast();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [editingUser, setEditingUser] = useState(null);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [userToDelete, setUserToDelete] = useState(null);
    const [deleteLoading, setDeleteLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        personal_quota: 1000,
        is_admin: false,
    });

    useEffect(() => {
        fetchUsers();
    }, []);

    async function fetchUsers() {
        try {
            setLoading(true);
            const data = await api.getUsers();
            // Map API response to expected format
            const mapped = data.map(user => ({
                user_id: user.id,
                name: user.name,
                email: user.email,
                personal_quota: user.personal_quota,
                used_tokens: user.used_tokens,
                remaining_tokens: user.available_quota,
                usage_percentage: user.personal_quota > 0
                    ? Math.round((user.used_tokens / user.personal_quota) * 100)
                    : 0,
                status: user.status,
                on_vacation: user.status === 'vacation',
                is_admin: false, // TODO: Add admin field to API
            }));
            setUsers(mapped);
        } catch (err) {
            // Surface the error and avoid using demo data silently
            setError(err?.message || 'Failed to load users');
            setUsers([]);
        } finally {
            setLoading(false);
        }
    }

    const filteredUsers = users.filter(user =>
        user.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    function openCreateModal() {
        setEditingUser(null);
        setFormData({ name: '', email: '', personal_quota: 1000, is_admin: false });
        setShowModal(true);
    }

    function openEditModal(user) {
        setEditingUser(user);
        setFormData({
            name: user.name,
            email: user.email,
            personal_quota: user.personal_quota,
            is_admin: user.is_admin || false,
        });
        setShowModal(true);
    }

    async function handleSubmit(e) {
        e.preventDefault();
        try {
            if (editingUser) {
                await api.updateUser(editingUser.user_id, formData);
                showToast({ type: 'success', title: 'User Updated', message: `${formData.name} has been updated` });
            } else {
                await api.createUser(formData);
                showToast({ type: 'success', title: 'User Created', message: `${formData.name} has been created` });
            }
            setShowModal(false);
            fetchUsers();
        } catch (err) {
            showToast({ type: 'error', title: 'Error', message: err.message || 'Failed to save user' });
        }
    }

    function openDeleteDialog(user) {
        setUserToDelete(user);
        setDeleteDialogOpen(true);
    }

    async function handleConfirmDelete() {
        if (!userToDelete) return;
        setDeleteLoading(true);
        try {
            await api.deleteUser(userToDelete.user_id);
            showToast({ type: 'success', title: 'User Deleted', message: `${userToDelete.name} has been deleted` });
            setDeleteDialogOpen(false);
            setUserToDelete(null);
            fetchUsers();
        } catch (err) {
            showToast({ type: 'error', title: 'Error', message: err.message || 'Failed to delete user' });
        } finally {
            setDeleteLoading(false);
        }
    }

    function getUsageColor(percentage) {
        if (percentage >= 90) return 'text-red-600 bg-red-100';
        if (percentage >= 70) return 'text-yellow-600 bg-yellow-100';
        return 'text-green-600 bg-green-100';
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div>
            <div className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Users</h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-1">Manage user accounts and quotas</p>
                </div>
                <button onClick={openCreateModal} className="btn btn-primary flex items-center">
                    <PlusIcon className="h-5 w-5 mr-2" />
                    Add User
                </button>
            </div>

            {error && (
                <div className="mb-4 p-3 bg-yellow-50 text-yellow-700 rounded-lg text-sm flex items-center justify-between">
                    <div>API error: {error}. Demo data not used.</div>
                    <div className="flex items-center space-x-2">
                        <button onClick={() => { setError(null); fetchUsers(); }} className="btn btn-primary">Retry</button>
                        <a href="mailto:support@example.com" className="btn btn-secondary">Contact Support</a>
                    </div>
                </div>
            )}

            {/* Search */}
            <div className="card mb-6">
                <div className="relative">
                    <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500 pointer-events-none" />
                    <input
                        type="text"
                        placeholder="Search users by name or email..."
                        className="input w-full pl-10"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            {/* Users Table */}
            <div className="card overflow-hidden">
                <table className="data-table">
                    <thead>
                        <tr>
                            <th>User</th>
                            <th>Quota</th>
                            <th>Usage</th>
                            <th>Status</th>
                            <th>Role</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                        {filteredUsers.map((user) => (
                            <tr key={user.user_id}>
                                <td>
                                    <div>
                                        <p className="font-medium text-gray-900 dark:text-white">{user.name}</p>
                                        <p className="text-sm text-gray-500 dark:text-gray-400">{user.email}</p>
                                    </div>
                                </td>
                                <td>
                                    <div>
                                        <p className="font-medium text-gray-900 dark:text-white">{user.used_tokens?.toLocaleString()} / {user.personal_quota?.toLocaleString()}</p>
                                        <p className="text-sm text-gray-500 dark:text-gray-400">{user.remaining_tokens?.toLocaleString()} remaining</p>
                                    </div>
                                </td>
                                <td>
                                    <div className="flex items-center">
                                        <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                                            <div
                                                className={`h-2 rounded-full ${user.usage_percentage >= 90 ? 'bg-red-500' : user.usage_percentage >= 70 ? 'bg-yellow-500' : 'bg-green-500'}`}
                                                style={{ width: `${Math.min(user.usage_percentage, 100)}%` }}
                                            ></div>
                                        </div>
                                        <span className={`badge ${getUsageColor(user.usage_percentage)}`}>
                                            {user.usage_percentage}%
                                        </span>
                                    </div>
                                </td>
                                <td>
                                    {user.on_vacation ? (
                                        <span className="badge badge-yellow">On Vacation</span>
                                    ) : (
                                        <span className="badge badge-green">Active</span>
                                    )}
                                </td>
                                <td>
                                    {user.is_admin ? (
                                        <span className="badge badge-blue">Admin</span>
                                    ) : (
                                        <span className="text-gray-500 dark:text-gray-400">User</span>
                                    )}
                                </td>
                                <td>
                                    <div className="flex space-x-2">
                                        <button
                                            onClick={() => openEditModal(user)}
                                            className="p-1 text-gray-400 hover:text-blue-600"
                                        >
                                            <PencilIcon className="h-5 w-5" />
                                        </button>
                                        <button
                                            onClick={() => openDeleteDialog(user)}
                                            className="p-1 text-gray-400 hover:text-red-600"
                                        >
                                            <TrashIcon className="h-5 w-5" />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Modal */}
            {
                showModal && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md p-6">
                            <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
                                {editingUser ? 'Edit User' : 'Add User'}
                            </h2>
                            <form onSubmit={handleSubmit}>
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Name</label>
                                        <input
                                            type="text"
                                            className="input"
                                            value={formData.name}
                                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Email</label>
                                        <input
                                            type="email"
                                            className="input"
                                            value={formData.email}
                                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Personal Quota</label>
                                        <input
                                            type="number"
                                            className="input"
                                            value={formData.personal_quota}
                                            onChange={(e) => setFormData({ ...formData, personal_quota: parseInt(e.target.value) })}
                                            required
                                        />
                                    </div>
                                    <div className="flex items-center">
                                        <input
                                            type="checkbox"
                                            id="is_admin"
                                            className="h-4 w-4 text-blue-600 rounded"
                                            checked={formData.is_admin}
                                            onChange={(e) => setFormData({ ...formData, is_admin: e.target.checked })}
                                        />
                                        <label htmlFor="is_admin" className="ml-2 text-sm text-gray-700 dark:text-gray-200">
                                            Administrator privileges
                                        </label>
                                    </div>
                                </div>
                                <div className="mt-6 flex justify-end space-x-3">
                                    <button
                                        type="button"
                                        onClick={() => setShowModal(false)}
                                        className="btn btn-secondary"
                                    >
                                        Cancel
                                    </button>
                                    <button type="submit" className="btn btn-primary">
                                        {editingUser ? 'Save Changes' : 'Create User'}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                )
            }

            {/* Delete Confirmation Dialog */}
            <DeleteConfirmDialog
                isOpen={deleteDialogOpen}
                onClose={() => { setDeleteDialogOpen(false); setUserToDelete(null); }}
                onConfirm={handleConfirmDelete}
                itemName={userToDelete?.name || ''}
                itemType="user"
                loading={deleteLoading}
            />
        </div >
    );
}
