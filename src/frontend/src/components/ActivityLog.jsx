import {
    ArrowsRightLeftIcon,
    ChartBarIcon,
    ClockIcon,
    CurrencyDollarIcon,
    FunnelIcon,
    UserMinusIcon,
    UserPlusIcon,
} from '@heroicons/react/24/outline';
import { useEffect, useState } from 'react';
import api from '../services/api';

const ACTIVITY_TYPES = {
    transfer: {
        icon: ArrowsRightLeftIcon,
        iconBg: 'bg-blue-100 dark:bg-blue-900/30',
        iconColor: 'text-blue-600 dark:text-blue-400',
        label: 'Reallocation',
    },
    user_created: {
        icon: UserPlusIcon,
        iconBg: 'bg-green-100 dark:bg-green-900/30',
        iconColor: 'text-green-600 dark:text-green-400',
        label: 'User Created',
    },
    user_removed: {
        icon: UserMinusIcon,
        iconBg: 'bg-red-100 dark:bg-red-900/30',
        iconColor: 'text-red-600 dark:text-red-400',
        label: 'User Removed',
    },
    quota_update: {
        icon: CurrencyDollarIcon,
        iconBg: 'bg-yellow-100 dark:bg-yellow-900/30',
        iconColor: 'text-yellow-600 dark:text-yellow-400',
        label: 'Quota Update',
    },
    usage: {
        icon: ChartBarIcon,
        iconBg: 'bg-purple-100 dark:bg-purple-900/30',
        iconColor: 'text-purple-600 dark:text-purple-400',
        label: 'Usage',
    },
};

// [AI GENERATED]
// Model: GitHub Copilot (GPT-4.1)
// Logic: formatRelativeTime formats timestamps as human-readable relative times for activity logs (e.g., "5 min ago").
// Why: Improves readability and context for recent activity events.
// Root Cause: Raw timestamps are hard to interpret quickly.
// Context: Used in activity log UI. Future: consider i18n and timezone support.
// Model Suitability: Relative time formatting is standard; GPT-4.1 is sufficient.
function formatRelativeTime(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return date.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
    }).replace(/\//g, '.');
}

// Demo data outside component to avoid re-creation
const DEMO_ACTIVITIES = [
    { id: 1, type: 'transfer', description: 'John reallocated 5,000 credits to Sarah for project deadline', timestamp: '2024-01-15T10:30:00Z', user: 'John Doe' },
    { id: 2, type: 'user_created', description: 'New user "Mike Chen" was added to Dev Team', timestamp: '2024-01-15T09:00:00Z', user: 'Admin' },
    { id: 3, type: 'quota_update', description: 'Monthly quota reset for all users', timestamp: '2024-01-14T18:00:00Z', user: 'System' },
    { id: 4, type: 'usage', description: 'Marketing Team consumed 15,000 credits today', timestamp: '2024-01-14T14:00:00Z', user: 'System' },
    { id: 5, type: 'transfer', description: 'Emma received 3,000 credits from Team Pool (vacation release)', timestamp: '2024-01-13T11:00:00Z', user: 'Emma Wilson' },
    { id: 6, type: 'user_removed', description: 'User "Alex Brown" was removed from system', timestamp: '2024-01-12T16:00:00Z', user: 'Admin' },
];

/**
 * ActivityLog - Shows recent activity in the system
 * 
 * @param {Array} activities - Array of activity objects
 * @param {string} title - Section title
 * @param {boolean} showFilter - Show filter dropdown
 * @param {number} limit - Max items to show
 */
export default function ActivityLog({
    activities = [],
    title = 'Recent Activity',
    showFilter = true,
    limit = 10,
}) {
    const [filter, setFilter] = useState('all');
    const [expanded, setExpanded] = useState(false);
    const [logData, setLogData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    // [AI GENERATED]
    // Model: GitHub Copilot (GPT-4.1)
    // Logic: Add inline editing state for activity descriptions.
    // Why: Implements the first quick win from the roadmap for better UX.
    // Root Cause: Activity descriptions were static and not editable.
    // Context: Allows users to click and edit activity descriptions inline.
    // Model Suitability: For more advanced collaborative editing, consider GPT-4 Turbo.
    const [editingId, setEditingId] = useState(null);
    const [editValue, setEditValue] = useState('');

    useEffect(() => {
        let mounted = true;
        setLoading(true);
        api.getAuditLogs(0, 100)
            .then(logs => {
                if (mounted) {
                    setLogData(logs.map(mapAuditLogToActivity));
                    setLoading(false);
                }
            })
            .catch(e => {
                if (mounted) {
                    setError(e.message || 'Failed to load activity log');
                    setLoading(false);
                }
            });
        return () => { mounted = false; };
    }, []);
    const data = activities.length > 0 ? activities : DEMO_ACTIVITIES;

    const filteredData = filter === 'all'
        ? data
        : data.filter(a => a.type === filter);

    const displayedData = expanded
        ? filteredData
        : filteredData.slice(0, limit);

    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
            {/* Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                <div className="flex items-center space-x-2">
                    <ClockIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
                    <h3 className="font-semibold text-gray-900 dark:text-white">{title}</h3>
                </div>
                {showFilter && (
                    <div className="relative">
                        <select
                            value={filter}
                            onChange={(e) => setFilter(e.target.value)}
                            className="appearance-none pl-8 pr-4 py-1.5 text-sm bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-200 focus:ring-2 focus:ring-[#1d3557] focus:border-transparent cursor-pointer"
                        >
                            <option value="all">All Activity</option>
                            <option value="transfer">Reallocations</option>
                            <option value="user_created">Users Created</option>
                            <option value="user_removed">Users Removed</option>
                            <option value="quota_update">Quota Updates</option>
                            <option value="usage">Usage</option>
                        </select>
                        <FunnelIcon className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500 pointer-events-none" />
                    </div>
                )}
            </div>

            {/* Activity List with Inline Editing */}
            <div className="divide-y divide-gray-100 dark:divide-gray-700">
                {displayedData.length === 0 ? (
                    <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                        No activity to display
                    </div>
                ) : (
                    displayedData.map((activity) => {
                        const config = ACTIVITY_TYPES[activity.type] || ACTIVITY_TYPES.usage;
                        const Icon = config.icon;
                        const isEditing = editingId === activity.id;
                        return (
                            <div
                                key={activity.id}
                                className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                            >
                                <div className="flex items-start space-x-3">
                                    <div className={`flex-shrink-0 p-2 rounded-lg ${config.iconBg}`}>
                                        <Icon className={`h-4 w-4 ${config.iconColor}`} />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        {isEditing ? (
                                            <form
                                                onSubmit={e => {
                                                    e.preventDefault();
                                                    // Save logic here (API call or local update)
                                                    activity.description = editValue;
                                                    setEditingId(null);
                                                }}
                                            >
                                                <input
                                                    className="text-sm text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 w-full"
                                                    value={editValue}
                                                    autoFocus
                                                    onChange={e => setEditValue(e.target.value)}
                                                    onBlur={() => setEditingId(null)}
                                                />
                                            </form>
                                        ) : (
                                            <p
                                                className="text-sm text-gray-900 dark:text-white cursor-pointer hover:underline"
                                                title="Click to edit"
                                                onClick={() => {
                                                    setEditingId(activity.id);
                                                    setEditValue(activity.description);
                                                }}
                                            >
                                                {activity.description}
                                            </p>
                                        )}
                                        <div className="flex items-center mt-1 space-x-2 text-xs text-gray-500 dark:text-gray-400">
                                            <span>{activity.user}</span>
                                            <span>•</span>
                                            <span>{formatRelativeTime(activity.timestamp)}</span>
                                        </div>
                                    </div>
                                    <span className={`flex-shrink-0 text-xs px-2 py-1 rounded-full ${config.iconBg} ${config.iconColor}`}>
                                        {config.label}
                                    </span>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>

            {/* Show More */}
            {filteredData.length > limit && (
                <div className="p-3 border-t border-gray-200 dark:border-gray-700">
                    <button
                        onClick={() => setExpanded(!expanded)}
                        className="w-full text-sm text-[#1d3557] dark:text-blue-400 hover:underline"
                    >
                        {expanded ? 'Show Less' : `Show ${filteredData.length - limit} More`}
                    </button>
                </div>
            )}
        </div>
    );
}
