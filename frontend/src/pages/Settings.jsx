import { useState, useEffect } from 'react';
import { useUser } from '../context/UserContext';
import {
    Cog6ToothIcon,
    BellIcon,
    GlobeAltIcon,
    ShieldCheckIcon,
    KeyIcon,
    DocumentTextIcon,
    ArrowDownTrayIcon,
    CheckCircleIcon,
} from '@heroicons/react/24/outline';

export default function Settings() {
    const { user } = useUser();
    const [saved, setSaved] = useState(false);

    // Settings state
    const [settings, setSettings] = useState(() => {
        const saved = localStorage.getItem('alfred_settings');
        return saved ? JSON.parse(saved) : {
            notifications: {
                email: true,
                browser: true,
                quotaWarning: true,
                weeklyReport: false,
            },
            display: {
                compactMode: false,
                showTokenCost: true,
                dateFormat: 'DD.MM.YYYY',
                language: 'en',
            },
            privacy: {
                shareUsageStats: false,
                showActivityStatus: true,
            },
        };
    });

    useEffect(() => {
        localStorage.setItem('alfred_settings', JSON.stringify(settings));
    }, [settings]);

    const handleToggle = (category, key) => {
        setSettings(prev => {
            const newSettings = {
                ...prev,
                [category]: {
                    ...prev[category],
                    [key]: !prev[category][key],
                }
            };
            // Show saved indicator
            setSaved(true);
            setTimeout(() => setSaved(false), 1500);
            return newSettings;
        });
    };

    const handleSelect = (category, key, value) => {
        setSettings(prev => {
            const newSettings = {
                ...prev,
                [category]: {
                    ...prev[category],
                    [key]: value,
                }
            };
            // Show saved indicator
            setSaved(true);
            setTimeout(() => setSaved(false), 1500);
            return newSettings;
        });
    };

    const handleSave = () => {
        localStorage.setItem('alfred_settings', JSON.stringify(settings));
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    const handleExportData = () => {
        const data = {
            user: user,
            settings: settings,
            exportedAt: new Date().toISOString(),
        };
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `alfred-settings-${new Date().toLocaleDateString('en-GB').replace(/\//g, '-')}.json`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const ToggleSwitch = ({ enabled, onToggle }) => (
        <button
            onClick={onToggle}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${enabled ? 'bg-[#1d3557]' : 'bg-gray-300 dark:bg-gray-600'
                }`}
        >
            <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${enabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
            />
        </button>
    );

    const SettingRow = ({ icon: Icon, label, description, children }) => (
        <div className="flex items-center justify-between py-4 border-b border-gray-700 last:border-b-0">
            <div className="flex items-start space-x-3">
                <Icon className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                    <p className="text-sm font-medium text-white">{label}</p>
                    {description && (
                        <p className="text-xs text-gray-400 mt-0.5">{description}</p>
                    )}
                </div>
            </div>
            <div className="ml-4">
                {children}
            </div>
        </div>
    );

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">Settings</h1>
                    <p className="text-gray-400 mt-1">
                        Manage your preferences and application settings
                    </p>
                </div>
                {saved && (
                    <span className="flex items-center px-3 py-1.5 rounded-lg text-sm bg-green-500/20 text-green-400">
                        <CheckCircleIcon className="h-4 w-4 mr-1.5" />
                        Saved
                    </span>
                )}
            </div>

            {/* Appearance Section */}
            <div className="bg-gray-800 rounded-xl shadow-sm border border-gray-700 p-6">
                <div className="flex items-center space-x-2 mb-4">
                    <Cog6ToothIcon className="h-5 w-5 text-blue-400" />
                    <h2 className="text-lg font-semibold text-white">Appearance</h2>
                </div>

                <SettingRow
                    icon={GlobeAltIcon}
                    label="Date Format"
                    description="Choose your preferred date format"
                >
                    <select
                        value={settings.display.dateFormat}
                        onChange={(e) => handleSelect('display', 'dateFormat', e.target.value)}
                        className="px-3 py-1.5 text-sm bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                        <option value="DD.MM.YYYY">DD.MM.YYYY</option>
                        <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                        <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                    </select>
                </SettingRow>
            </div>

            {/* Notifications Section */}
            <div className="bg-gray-800 rounded-xl shadow-sm border border-gray-700 p-6">
                <div className="flex items-center space-x-2 mb-4">
                    <BellIcon className="h-5 w-5 text-blue-400" />
                    <h2 className="text-lg font-semibold text-white">Notifications</h2>
                </div>

                <SettingRow
                    icon={BellIcon}
                    label="Email Notifications"
                    description="Receive important updates via email"
                >
                    <ToggleSwitch
                        enabled={settings.notifications.email}
                        onToggle={() => handleToggle('notifications', 'email')}
                    />
                </SettingRow>

                <SettingRow
                    icon={BellIcon}
                    label="Browser Notifications"
                    description="Show desktop notifications"
                >
                    <ToggleSwitch
                        enabled={settings.notifications.browser}
                        onToggle={() => handleToggle('notifications', 'browser')}
                    />
                </SettingRow>

                <SettingRow
                    icon={BellIcon}
                    label="Quota Warning"
                    description="Alert when quota usage exceeds 80%"
                >
                    <ToggleSwitch
                        enabled={settings.notifications.quotaWarning}
                        onToggle={() => handleToggle('notifications', 'quotaWarning')}
                    />
                </SettingRow>

                <SettingRow
                    icon={BellIcon}
                    label="Weekly Report"
                    description="Receive weekly usage summary"
                >
                    <ToggleSwitch
                        enabled={settings.notifications.weeklyReport}
                        onToggle={() => handleToggle('notifications', 'weeklyReport')}
                    />
                </SettingRow>
            </div>

            {/* Privacy Section */}
            <div className="bg-gray-800 rounded-xl shadow-sm border border-gray-700 p-6">
                <div className="flex items-center space-x-2 mb-4">
                    <ShieldCheckIcon className="h-5 w-5 text-blue-400" />
                    <h2 className="text-lg font-semibold text-white">Privacy</h2>
                </div>

                <SettingRow
                    icon={ShieldCheckIcon}
                    label="Share Usage Statistics"
                    description="Help improve Alfred by sharing anonymous usage data"
                >
                    <ToggleSwitch
                        enabled={settings.privacy.shareUsageStats}
                        onToggle={() => handleToggle('privacy', 'shareUsageStats')}
                    />
                </SettingRow>

                <SettingRow
                    icon={ShieldCheckIcon}
                    label="Show Activity Status"
                    description="Let others see when you're online"
                >
                    <ToggleSwitch
                        enabled={settings.privacy.showActivityStatus}
                        onToggle={() => handleToggle('privacy', 'showActivityStatus')}
                    />
                </SettingRow>
            </div>

            {/* Data Section */}
            <div className="bg-gray-800 rounded-xl shadow-sm border border-gray-700 p-6">
                <div className="flex items-center space-x-2 mb-4">
                    <KeyIcon className="h-5 w-5 text-blue-400" />
                    <h2 className="text-lg font-semibold text-white">Data & Security</h2>
                </div>

                <SettingRow
                    icon={ArrowDownTrayIcon}
                    label="Export Settings"
                    description="Download your settings as a JSON file"
                >
                    <button
                        onClick={handleExportData}
                        className="px-4 py-1.5 text-sm bg-gray-700 hover:bg-gray-600 text-gray-200 rounded-lg transition-colors"
                    >
                        Export
                    </button>
                </SettingRow>

                <SettingRow
                    icon={KeyIcon}
                    label="API Key"
                    description="Your current session API key"
                >
                    <code className="px-3 py-1 text-xs bg-gray-700 text-gray-300 rounded font-mono">
                        ••••••••••••
                    </code>
                </SettingRow>
            </div>

            {/* Version Info */}
            <div className="text-center text-sm text-gray-400 py-4">
                Alfred v1.0.0 | Built with React + Vite + TailwindCSS
            </div>
        </div>
    );
}
