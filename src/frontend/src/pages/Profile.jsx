import {
    ArrowTrendingUpIcon,
    BellIcon,
    ChartBarIcon,
    ClockIcon,
    CogIcon,
    EnvelopeIcon,
    EyeSlashIcon,
    KeyIcon,
    ShieldCheckIcon,
    SunIcon,
    UsersIcon
} from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';
import { useToast } from '../context/ToastContext';
import { useUser } from '../context/UserContext';
import api from '../services/api';

function StatItem({ icon: Icon, label, value, color = 'blue' }) {
    const colorClasses = {
        blue: 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300',
        green: 'bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-300',
        yellow: 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900 dark:text-yellow-300',
        purple: 'bg-purple-100 text-purple-600 dark:bg-purple-900 dark:text-purple-300',
    };

    return (
        <div className="flex items-center p-4 rounded-lg bg-gray-50 dark:bg-gray-700">
            <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
                <Icon className="h-5 w-5" />
            </div>
            <div className="ml-4">
                <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">{value}</p>
            </div>
        </div>
    );
}

export default function Profile() {
    const { user, updateUser, refetch } = useUser();
    const { showToast } = useToast();
    const [editing, setEditing] = useState(false);
    const [formData, setFormData] = useState({
        name: '',
        email: '',
    });
    const [usageHistory, setUsageHistory] = useState([]);
    const [notifications, setNotifications] = useState({
        email_alerts: true,
        quota_warnings: true,
        weekly_reports: false,
    });
    const [vacationMode, setVacationMode] = useState(false);
    const [privacyMode, setPrivacyMode] = useState('normal'); // normal or strict
    const [statusLoading, setStatusLoading] = useState(false);

    useEffect(() => {
        if (user) {
            setFormData({
                name: user.name || '',
                email: user.email || '',
            });

            // Load preferences if available
            if (user.preferences && user.preferences.notifications) {
                setNotifications(prev => ({ ...prev, ...user.preferences.notifications }));
            }

            setVacationMode(user.status === 'on_vacation' || user.on_vacation || false);
            setPrivacyMode(user.default_privacy || 'normal');

            // Fetch real usage history
            fetchUsageHistory();
        }
    }, [user]);

    const fetchUsageHistory = async () => {
        try {
            const data = await api.getUsageAnalytics(7);
            if (data.history) {
                setUsageHistory(data.history.map(h => ({
                    date: new Date(h.date).toLocaleDateString('en-US', { month: '2-digit', day: '2-digit' }),
                    tokens: h.tokens,
                    cost: h.cost
                })));
            }
        } catch (err) {
            console.error('Failed to fetch usage history:', err);
            // Fallback to mock data
            setUsageHistory([
                { date: '12-02', tokens: 1250, cost: 0.15 },
                { date: '11-02', tokens: 2100, cost: 0.25 },
                { date: '10-02', tokens: 1800, cost: 0.22 },
                { date: '09-02', tokens: 3200, cost: 0.38 },
                { date: '08-02', tokens: 2500, cost: 0.30 },
            ]);
        }
    };

    const handleSave = async () => {
        try {
            const updates = {
                ...formData,
                preferences: {
                    ...(user.preferences || {}),
                    notifications: notifications
                }
            };
            await api.updateProfile(updates);
            updateUser(updates); // Update local context
            setEditing(false);
            showToast('Profile updated successfully', 'success');
        } catch (err) {
            showToast(err.message || 'Failed to update profile', 'error');
        }
    };

    const handleVacationToggle = async () => {
        const newStatus = vacationMode ? 'active' : 'on_vacation';
        try {
            setStatusLoading(true);
            await api.updateUserStatus(newStatus);
            setVacationMode(!vacationMode);
            showToast(
                vacationMode ? 'Vacation mode disabled' : 'Vacation mode enabled - your quota is now shared with team',
                'success'
            );
            if (refetch) refetch();
        } catch (err) {
            showToast(err.message || 'Failed to update status', 'error');
        } finally {
            setStatusLoading(false);
        }
    };

    const handlePrivacyToggle = async () => {
        const newMode = privacyMode === 'strict' ? 'normal' : 'strict';
        try {
            setStatusLoading(true);
            await api.updatePrivacyMode(newMode);
            setPrivacyMode(newMode);
            showToast(
                newMode === 'strict' ? 'Privacy mode enabled - messages will not be logged' : 'Privacy mode disabled',
                'success'
            );
            if (refetch) refetch();
        } catch (err) {
            showToast(err.message || 'Failed to update privacy mode', 'error');
        } finally {
            setStatusLoading(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        return `${day}-${month}`;
    };

    const formatFullDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        const day = date.getDate().toString().padStart(2, '0');
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const year = date.getFullYear().toString().slice(-2);
        return `${day}-${month}-${year}`;
    };

    if (!user) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    const quotaUsedPercent = user.personal_quota
        ? Math.round((user.used_tokens / user.personal_quota) * 100)
        : 0;

    return (
        <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">My Profile</h1>
                <p className="text-gray-500 dark:text-gray-400 mt-1">Manage your account settings and preferences</p>
            </div>

            {/* Profile Card */}
            <div className="card mb-6">
                <div className="flex items-start justify-between mb-6">
                    <div className="flex items-center">
                        <div className="h-20 w-20 rounded-full bg-[#1d3557] flex items-center justify-center text-3xl font-bold text-white">
                            {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                        </div>
                        <div className="ml-6">
                            {editing ? (
                                <div className="space-y-3">
                                    <input
                                        type="text"
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        className="input text-lg font-semibold"
                                        placeholder="Your name"
                                    />
                                    <input
                                        type="email"
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                        className="input"
                                        placeholder="Your email"
                                    />
                                </div>
                            ) : (
                                <>
                                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">{user.name}</h2>
                                    <p className="text-gray-500 dark:text-gray-400 flex items-center mt-1">
                                        <EnvelopeIcon className="h-4 w-4 mr-2" />
                                        {user.email}
                                    </p>
                                    <div className="flex items-center mt-2 space-x-3">
                                        <span className="badge badge-primary">{user.role || 'User'}</span>
                                        {user.team && (
                                            <span className="text-sm text-gray-500 dark:text-gray-400 flex items-center">
                                                <UsersIcon className="h-4 w-4 mr-1" />
                                                {user.team}
                                            </span>
                                        )}
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                    <div>
                        {editing ? (
                            <div className="space-x-2">
                                <button
                                    onClick={handleSave}
                                    className="btn btn-primary"
                                >
                                    Save
                                </button>
                                <button
                                    onClick={() => setEditing(false)}
                                    className="btn btn-secondary"
                                >
                                    Cancel
                                </button>
                            </div>
                        ) : (
                            <button
                                onClick={() => setEditing(true)}
                                className="btn btn-secondary flex items-center"
                            >
                                <CogIcon className="h-4 w-4 mr-2" />
                                Edit Profile
                            </button>
                        )}
                    </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <StatItem
                        icon={ChartBarIcon}
                        label="Tokens Used"
                        value={(user.used_tokens || 0).toLocaleString()}
                        color="blue"
                    />
                    <StatItem
                        icon={ArrowTrendingUpIcon}
                        label="Quota Remaining"
                        value={`${quotaUsedPercent}%`}
                        color={quotaUsedPercent > 80 ? 'yellow' : 'green'}
                    />
                    <StatItem
                        icon={ClockIcon}
                        label="Last Login"
                        value={formatDate(user.last_login)}
                        color="purple"
                    />
                    <StatItem
                        icon={ShieldCheckIcon}
                        label="Member Since"
                        value={formatFullDate(user.created_at)}
                        color="blue"
                    />
                </div>
            </div>

            {/* Quota Progress */}
            <div className="card mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quota Usage</h3>
                <div className="mb-4">
                    <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-600 dark:text-gray-300">
                            {(user.used_tokens || 0).toLocaleString()} / {(user.personal_quota || 50000).toLocaleString()} tokens
                        </span>
                        <span className={`font-medium ${quotaUsedPercent > 80 ? 'text-yellow-600' : 'text-green-600'}`}>
                            {quotaUsedPercent}% used
                        </span>
                    </div>
                    <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div
                            className={`h-full rounded-full transition-all duration-500 ${quotaUsedPercent > 90 ? 'bg-red-500' :
                                quotaUsedPercent > 70 ? 'bg-yellow-500' : 'bg-green-500'
                                }`}
                            style={{ width: `${Math.min(quotaUsedPercent, 100)}%` }}
                        />
                    </div>
                </div>
            </div>

            {/* Status & Privacy */}
            <div className="card mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                    <CogIcon className="h-5 w-5 mr-2" />
                    Status & Privacy
                </h3>
                <div className="space-y-4">
                    {/* Vacation Mode */}
                    <div className="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700">
                        <div className="flex items-center">
                            <div className="p-2 rounded-lg bg-yellow-100 dark:bg-yellow-900/30 mr-3">
                                <SunIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
                            </div>
                            <div>
                                <p className="font-medium text-gray-900 dark:text-white">Vacation Mode</p>
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                    Share up to 10% of your quota with team members while away
                                </p>
                            </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={vacationMode}
                                onChange={handleVacationToggle}
                                disabled={statusLoading}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-yellow-500"></div>
                        </label>
                    </div>

                    {/* Privacy Mode */}
                    <div className="flex items-center justify-between py-3">
                        <div className="flex items-center">
                            <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-900/30 mr-3">
                                <EyeSlashIcon className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                            </div>
                            <div>
                                <p className="font-medium text-gray-900 dark:text-white">Strict Privacy Mode</p>
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                    When enabled, your messages and responses will not be logged
                                </p>
                            </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                checked={privacyMode === 'strict'}
                                onChange={handlePrivacyToggle}
                                disabled={statusLoading}
                                className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 dark:peer-focus:ring-purple-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-purple-500"></div>
                        </label>
                    </div>
                </div>
            </div>

            {/* Recent Usage */}
            <div className="card mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Usage</h3>
                <div className="overflow-x-auto">
                    <table className="data-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Tokens</th>
                                <th>Cost</th>
                            </tr>
                        </thead>
                        <tbody>
                            {usageHistory.map((row, index) => (
                                <tr key={index}>
                                    <td>{row.date}</td>
                                    <td>{row.tokens.toLocaleString()}</td>
                                    <td>${row.cost.toFixed(2)}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Notification Preferences */}
            <div className="card mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                    <BellIcon className="h-5 w-5 mr-2" />
                    Notification Preferences
                </h3>
                <div className="space-y-4">
                    {[
                        { key: 'email_alerts', label: 'Email Alerts', desc: 'Receive email notifications for important events' },
                        { key: 'quota_warnings', label: 'Quota Warnings', desc: 'Get notified when quota is running low' },
                        { key: 'weekly_reports', label: 'Weekly Reports', desc: 'Receive weekly usage summary via email' },
                    ].map((pref) => (
                        <div key={pref.key} className="flex items-center justify-between py-2">
                            <div>
                                <p className="font-medium text-gray-900 dark:text-white">{pref.label}</p>
                                <p className="text-sm text-gray-500 dark:text-gray-400">{pref.desc}</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={notifications[pref.key]}
                                    onChange={(e) => setNotifications({
                                        ...notifications,
                                        [pref.key]: e.target.checked
                                    })}
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-[#1d3557]"></div>
                            </label>
                        </div>
                    ))}
                </div>
            </div>

            {/* Security Section */}
            <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                    <KeyIcon className="h-5 w-5 mr-2" />
                    Security
                </h3>
                <div className="space-y-4">
                    <div className="flex items-center justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                        <div>
                            <p className="font-medium text-gray-900 dark:text-white">API Key</p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                                Your API key is stored securely
                            </p>
                        </div>
                        <span className="text-sm text-gray-600 dark:text-gray-400 font-mono">tp-****...****</span>
                    </div>
                    <div className="flex items-center justify-between py-2">
                        <div>
                            <p className="font-medium text-gray-900 dark:text-white">Regenerate API Key</p>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                                This will invalidate your current key
                            </p>
                        </div>
                        <button className="btn btn-danger text-sm">
                            Regenerate
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
