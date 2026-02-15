import {
    MagnifyingGlassIcon,
    PencilIcon,
    PlusIcon,
    TrashIcon,
    UserMinusIcon,
    UserPlusIcon,
} from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';
import DeleteConfirmDialog from '../components/DeleteConfirmDialog';
import { useToast } from '../context/ToastContext';
import api from '../services/api';

export default function Teams() {
    const { showToast } = useToast();
    const [teams, setTeams] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [showModal, setShowModal] = useState(false);
    const [showMemberModal, setShowMemberModal] = useState(false);
    const [editingTeam, setEditingTeam] = useState(null);
    const [selectedTeam, setSelectedTeam] = useState(null);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [teamToDelete, setTeamToDelete] = useState(null);
    const [deleteLoading, setDeleteLoading] = useState(false);
    const [memberEmail, setMemberEmail] = useState('');
    const [teamMembers, setTeamMembers] = useState([]);
    const [membersLoading, setMembersLoading] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        pool_quota: 10000,
    });

    useEffect(() => {
        fetchTeams();
    }, []);

    async function fetchTeams() {
        try {
            setLoading(true);
            const data = await api.getTeams();
            // Map API response to expected format
            const mapped = data.map(team => ({
                team_id: team.id,
                team_name: team.name,
                description: team.description,
                pool_quota: team.common_pool,
                used_tokens: team.used_pool,
                remaining_tokens: team.available_pool,
                usage_percentage: team.common_pool > 0
                    ? Math.round((team.used_pool / team.common_pool) * 100)
                    : 0,
                member_count: team.member_count,
            }));
            setTeams(mapped);
        } catch (err) {
            // Surface the error and avoid silently populating demo data
            setError(err?.message || 'Failed to load teams');
            setTeams([]);
        } finally {
            setLoading(false);
        }
    }

    function openCreateModal() {
        setEditingTeam(null);
        setFormData({ name: '', pool_quota: 10000 });
        setShowModal(true);
    }

    function openEditModal(team) {
        setEditingTeam(team);
        setFormData({
            name: team.team_name,
            pool_quota: team.pool_quota,
        });
        setShowModal(true);
    }

    async function openMemberModal(team) {
        setSelectedTeam(team);
        setMemberEmail('');
        setTeamMembers([]);
        setShowMemberModal(true);
        // Fetch team members
        setMembersLoading(true);
        try {
            const members = await api.getTeamMembers(team.team_id);
            setTeamMembers(members || []);
        } catch (err) {
            // Don't populate demo members silently
            setTeamMembers([]);
            setError(err?.message || 'Failed to load team members');
        } finally {
            setMembersLoading(false);
        }
    }

    async function handleAddMember(e) {
        e.preventDefault();
        if (!memberEmail.trim()) return;
        try {
            await api.addTeamMember(selectedTeam.team_id, memberEmail);
            showToast({ type: 'success', title: 'Member Added', message: `${memberEmail} added to the team` });
            setMemberEmail('');
            // Refresh members
            const members = await api.getTeamMembers(selectedTeam.team_id);
            setTeamMembers(members || []);
            fetchTeams(); // Refresh team count
        } catch (err) {
            showToast({ type: 'error', title: 'Error', message: err.message || 'Failed to add member' });
        }
    }

    async function handleRemoveMember(memberId, memberName) {
        try {
            await api.removeTeamMember(selectedTeam.team_id, memberId);
            showToast({ type: 'success', title: 'Member Removed', message: `${memberName} removed from the team` });
            setTeamMembers(prev => prev.filter(m => m.id !== memberId));
            fetchTeams(); // Refresh team count
        } catch (err) {
            showToast({ type: 'error', title: 'Error', message: err.message || 'Failed to remove member' });
        }
    }

    async function handleSubmit(e) {
        e.preventDefault();
        try {
            if (editingTeam) {
                await api.updateTeam(editingTeam.team_id, formData);
                showToast({ type: 'success', title: 'Team Updated', message: `${formData.name} has been updated` });
            } else {
                await api.createTeam(formData);
                showToast({ type: 'success', title: 'Team Created', message: `${formData.name} has been created` });
            }
            setShowModal(false);
            fetchTeams();
        } catch (err) {
            showToast({ type: 'error', title: 'Error', message: err.message || 'Failed to save team' });
        }
    }

    function openDeleteDialog(team) {
        setTeamToDelete(team);
        setDeleteDialogOpen(true);
    }

    async function handleConfirmDelete() {
        if (!teamToDelete) return;
        setDeleteLoading(true);
        try {
            await api.deleteTeam(teamToDelete.team_id);
            showToast({ type: 'success', title: 'Team Deleted', message: `${teamToDelete.team_name} has been deleted` });
            setDeleteDialogOpen(false);
            setTeamToDelete(null);
            fetchTeams();
        } catch (err) {
            showToast({ type: 'error', title: 'Error', message: err.message || 'Failed to delete team' });
        } finally {
            setDeleteLoading(false);
        }
    }

    function getUsageColor(percentage) {
        if (percentage >= 90) return 'bg-red-500';
        if (percentage >= 70) return 'bg-yellow-500';
        return 'bg-green-500';
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
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Teams</h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-1">Manage team pools and members</p>
                </div>
                <button onClick={openCreateModal} className="btn btn-primary flex items-center">
                    <PlusIcon className="h-5 w-5 mr-2" />
                    Create Team
                </button>
            </div>

            {error && (
                <div className="mb-4 p-3 bg-yellow-50 text-yellow-700 rounded-lg text-sm flex items-center justify-between">
                    <div>API error: {error}. Demo data not used.</div>
                    <div className="flex items-center space-x-2">
                        <button onClick={() => { setError(null); fetchTeams(); }} className="btn btn-primary">Retry</button>
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
                        placeholder="Search teams by name..."
                        className="input w-full pl-10"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
            </div>

            {/* Teams Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {teams.filter(team =>
                    team.team_name?.toLowerCase().includes(searchTerm.toLowerCase())
                ).map((team) => (
                    <div key={team.team_id} className="card">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{team.team_name}</h3>
                                <p className="text-sm text-gray-500 dark:text-gray-400">{team.member_count} members</p>
                            </div>
                            <div className="flex space-x-1">
                                <button
                                    onClick={() => openMemberModal(team)}
                                    className="p-1 text-gray-400 hover:text-blue-600"
                                    title="Manage members"
                                >
                                    <UserPlusIcon className="h-5 w-5" />
                                </button>
                                <button
                                    onClick={() => openEditModal(team)}
                                    className="p-1 text-gray-400 hover:text-blue-600"
                                    title="Edit team"
                                >
                                    <PencilIcon className="h-5 w-5" />
                                </button>
                                <button
                                    onClick={() => openDeleteDialog(team)}
                                    className="p-1 text-gray-400 hover:text-red-600"
                                    title="Delete team"
                                >
                                    <TrashIcon className="h-5 w-5" />
                                </button>
                            </div>
                        </div>

                        {/* Usage bar */}
                        <div className="mb-4">
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-gray-500 dark:text-gray-400">Pool Usage</span>
                                <span className="font-medium text-gray-900 dark:text-white">{team.usage_percentage}%</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-3">
                                <div
                                    className={`h-3 rounded-full ${getUsageColor(team.usage_percentage)}`}
                                    style={{ width: `${Math.min(team.usage_percentage, 100)}%` }}
                                ></div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <p className="text-gray-500 dark:text-gray-400">Used</p>
                                <p className="font-semibold text-gray-900 dark:text-white">{team.used_tokens?.toLocaleString()}</p>
                            </div>
                            <div>
                                <p className="text-gray-500 dark:text-gray-400">Remaining</p>
                                <p className="font-semibold text-gray-900 dark:text-white">{team.remaining_tokens?.toLocaleString()}</p>
                            </div>
                            <div className="col-span-2">
                                <p className="text-gray-500 dark:text-gray-400">Total Quota</p>
                                <p className="font-semibold text-gray-900 dark:text-white">{team.pool_quota?.toLocaleString()}</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Create/Edit Team Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md p-6">
                        <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
                            {editingTeam ? 'Edit Team' : 'Create Team'}
                        </h2>
                        <form onSubmit={handleSubmit}>
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Team Name</label>
                                    <input
                                        type="text"
                                        className="input"
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Pool Quota</label>
                                    <input
                                        type="number"
                                        className="input"
                                        value={formData.pool_quota}
                                        onChange={(e) => setFormData({ ...formData, pool_quota: parseInt(e.target.value) })}
                                        required
                                    />
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
                                    {editingTeam ? 'Save Changes' : 'Create Team'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Member Management Modal */}
            {showMemberModal && selectedTeam && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-gray-800 rounded-lg shadow-xl w-full max-w-lg p-6 border border-gray-700">
                        <h2 className="text-xl font-bold mb-4 text-white">
                            Manage Members - {selectedTeam.team_name}
                        </h2>
                        <p className="text-gray-400 mb-4">
                            Add or remove team members.
                        </p>

                        {/* Add member form */}
                        <form onSubmit={handleAddMember} className="flex space-x-2 mb-6">
                            <input
                                type="email"
                                placeholder="Enter user email..."
                                className="input flex-1"
                                value={memberEmail}
                                onChange={(e) => setMemberEmail(e.target.value)}
                                required
                            />
                            <button type="submit" className="btn btn-primary">
                                <UserPlusIcon className="h-5 w-5" />
                            </button>
                        </form>

                        {/* Member list */}
                        <div className="border border-gray-700 rounded-lg divide-y divide-gray-700 max-h-64 overflow-y-auto">
                            {membersLoading ? (
                                <div className="p-4 text-center text-gray-400">Loading members...</div>
                            ) : teamMembers.length === 0 ? (
                                <div className="p-4 text-center text-gray-400">No members yet</div>
                            ) : (
                                teamMembers.map((member) => (
                                    <div key={member.id} className="p-3 flex items-center justify-between">
                                        <div>
                                            <p className="font-medium text-white">{member.name}</p>
                                            <p className="text-sm text-gray-400">{member.email}</p>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <span className={`badge ${member.is_admin ? 'badge-blue' : 'badge-green'}`}>
                                                {member.is_admin ? 'Admin' : 'Member'}
                                            </span>
                                            <button
                                                onClick={() => handleRemoveMember(member.id, member.name)}
                                                className="p-1 text-gray-400 hover:text-red-600"
                                                title="Remove member"
                                            >
                                                <UserMinusIcon className="h-5 w-5" />
                                            </button>
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>

                        <div className="mt-6 flex justify-end">
                            <button
                                onClick={() => setShowMemberModal(false)}
                                className="btn btn-secondary"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Delete Confirmation Dialog */}
            <DeleteConfirmDialog
                isOpen={deleteDialogOpen}
                onClose={() => { setDeleteDialogOpen(false); setTeamToDelete(null); }}
                onConfirm={handleConfirmDelete}
                itemName={teamToDelete?.team_name || ''}
                itemType="team"
                loading={deleteLoading}
            />
        </div>
    );
}
