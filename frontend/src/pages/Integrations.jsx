import { useState, useEffect } from 'react';
import {
    PlusIcon,
    TrashIcon,
    CheckCircleIcon,
    XCircleIcon,
    ArrowPathIcon,
} from '@heroicons/react/24/outline';
import { useToast } from '../context/ToastContext';

const INTEGRATION_TYPES = [
    {
        id: 'make',
        name: 'Make (Integromat)',
        description: 'Connect to Make.com for workflow automation',
        icon: '🔧',
        fields: [
            { name: 'webhook_url', label: 'Webhook URL', type: 'url', placeholder: 'https://hook.make.com/...' },
        ],
    },
    {
        id: 'slack',
        name: 'Slack',
        description: 'Send notifications to Slack channels',
        icon: '💬',
        fields: [
            { name: 'webhook_url', label: 'Webhook URL', type: 'url', placeholder: 'https://hooks.slack.com/services/...' },
            { name: 'channel', label: 'Channel', type: 'text', placeholder: '#general' },
        ],
    },
    {
        id: 'teams',
        name: 'Microsoft Teams',
        description: 'Send notifications to Teams channels',
        icon: '👥',
        fields: [
            { name: 'webhook_url', label: 'Webhook URL', type: 'url', placeholder: 'https://outlook.office.com/webhook/...' },
        ],
    },
    {
        id: 'telegram',
        name: 'Telegram',
        description: 'Send notifications via Telegram bot',
        icon: '✈️',
        fields: [
            { name: 'bot_token', label: 'Bot Token', type: 'password', placeholder: '123456789:ABC...' },
            { name: 'chat_id', label: 'Chat ID', type: 'text', placeholder: '-1001234567890' },
        ],
    },
    {
        id: 'whatsapp',
        name: 'WhatsApp',
        description: 'Send notifications via WhatsApp Business API',
        icon: '📱',
        fields: [
            { name: 'api_url', label: 'API URL', type: 'url', placeholder: 'https://api.whatsapp.com/...' },
            { name: 'api_key', label: 'API Key', type: 'password', placeholder: 'Your API key' },
            { name: 'phone_number', label: 'Phone Number', type: 'tel', placeholder: '+1234567890' },
        ],
    },
];

export default function Integrations() {
    const { showToast } = useToast();
    const [integrations, setIntegrations] = useState(() => {
        const saved = localStorage.getItem('alfred_integrations');
        return saved ? JSON.parse(saved) : [];
    });
    const [showModal, setShowModal] = useState(false);
    const [selectedType, setSelectedType] = useState(null);
    const [formData, setFormData] = useState({});
    const [testing, setTesting] = useState(null);

    useEffect(() => {
        localStorage.setItem('alfred_integrations', JSON.stringify(integrations));
    }, [integrations]);

    const openAddModal = (type) => {
        setSelectedType(type);
        const initialData = {};
        type.fields.forEach(field => {
            initialData[field.name] = '';
        });
        initialData.enabled = true;
        setFormData(initialData);
        setShowModal(true);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        const newIntegration = {
            id: Date.now().toString(),
            type: selectedType.id,
            name: selectedType.name,
            icon: selectedType.icon,
            config: { ...formData },
            status: 'pending',
            lastTested: null,
        };
        setIntegrations(prev => [...prev, newIntegration]);
        showToast({ type: 'success', title: 'Integration Added', message: `${selectedType.name} integration has been added` });
        setShowModal(false);
        setSelectedType(null);
    };

    const handleDelete = (id) => {
        setIntegrations(prev => prev.filter(i => i.id !== id));
        showToast({ type: 'success', title: 'Integration Removed', message: 'Integration has been removed' });
    };

    const handleToggle = (id) => {
        setIntegrations(prev => prev.map(i =>
            i.id === id ? { ...i, config: { ...i.config, enabled: !i.config.enabled } } : i
        ));
    };

    const testConnection = async (integration) => {
        setTesting(integration.id);
        // Simulate API test
        await new Promise(resolve => setTimeout(resolve, 2000));

        // For demo, randomly succeed or fail
        const success = Math.random() > 0.3;
        setIntegrations(prev => prev.map(i =>
            i.id === integration.id
                ? { ...i, status: success ? 'connected' : 'error', lastTested: new Date().toISOString() }
                : i
        ));

        if (success) {
            showToast({ type: 'success', title: 'Connection Successful', message: `${integration.name} is connected and working` });
        } else {
            showToast({ type: 'error', title: 'Connection Failed', message: `Failed to connect to ${integration.name}. Please check your credentials.` });
        }
        setTesting(null);
    };

    const getStatusBadge = (status) => {
        switch (status) {
            case 'connected':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-900/40 text-green-400">
                        <CheckCircleIcon className="h-3.5 w-3.5 mr-1" />
                        Connected
                    </span>
                );
            case 'error':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-900/40 text-red-400">
                        <XCircleIcon className="h-3.5 w-3.5 mr-1" />
                        Error
                    </span>
                );
            default:
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-900/40 text-yellow-400">
                        Pending Test
                    </span>
                );
        }
    };

    const availableTypes = INTEGRATION_TYPES.filter(
        type => !integrations.some(i => i.type === type.id)
    );

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-white">Integrations</h1>
                <p className="text-gray-400 mt-1">
                    Connect Alfred with external services for notifications and automation
                </p>
            </div>

            {/* Connected Integrations */}
            {integrations.length > 0 && (
                <div className="bg-gray-800 rounded-xl shadow-sm border border-gray-700 p-6">
                    <h2 className="text-lg font-semibold text-white mb-4">Connected Integrations</h2>
                    <div className="space-y-4">
                        {integrations.map((integration) => (
                            <div
                                key={integration.id}
                                className="flex items-center justify-between p-4 bg-gray-700/50 rounded-lg border border-gray-600"
                            >
                                <div className="flex items-center space-x-4">
                                    <span className="text-2xl">{integration.icon}</span>
                                    <div>
                                        <p className="font-medium text-white">{integration.name}</p>
                                        <div className="flex items-center space-x-3 mt-1">
                                            {getStatusBadge(integration.status)}
                                            {integration.lastTested && (
                                                <span className="text-xs text-gray-400">
                                                    Last tested: {new Date(integration.lastTested).toLocaleString()}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center space-x-2">
                                    {/* Enable/Disable Toggle */}
                                    <button
                                        onClick={() => handleToggle(integration.id)}
                                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${integration.config.enabled ? 'bg-[#1d3557]' : 'bg-gray-600'
                                            }`}
                                    >
                                        <span
                                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${integration.config.enabled ? 'translate-x-6' : 'translate-x-1'
                                                }`}
                                        />
                                    </button>

                                    {/* Test Connection */}
                                    <button
                                        onClick={() => testConnection(integration)}
                                        disabled={testing === integration.id}
                                        className="p-2 text-gray-400 hover:text-blue-400 transition-colors disabled:opacity-50"
                                        title="Test connection"
                                    >
                                        <ArrowPathIcon className={`h-5 w-5 ${testing === integration.id ? 'animate-spin' : ''}`} />
                                    </button>

                                    {/* Delete */}
                                    <button
                                        onClick={() => handleDelete(integration.id)}
                                        className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                                        title="Remove integration"
                                    >
                                        <TrashIcon className="h-5 w-5" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Available Integrations */}
            <div className="bg-gray-800 rounded-xl shadow-sm border border-gray-700 p-6">
                <h2 className="text-lg font-semibold text-white mb-4">
                    {integrations.length > 0 ? 'Add More Integrations' : 'Available Integrations'}
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {availableTypes.map((type) => (
                        <button
                            key={type.id}
                            onClick={() => openAddModal(type)}
                            className="flex items-start p-4 bg-gray-700/30 hover:bg-gray-700/60 rounded-lg border border-gray-600 hover:border-blue-500 transition-all text-left group"
                        >
                            <span className="text-3xl mr-4">{type.icon}</span>
                            <div className="flex-1">
                                <p className="font-medium text-white group-hover:text-blue-400 transition-colors">
                                    {type.name}
                                </p>
                                <p className="text-sm text-gray-400 mt-1">{type.description}</p>
                            </div>
                            <PlusIcon className="h-5 w-5 text-gray-400 group-hover:text-blue-400 transition-colors" />
                        </button>
                    ))}
                </div>
                {availableTypes.length === 0 && (
                    <p className="text-center text-gray-400 py-4">
                        All available integrations have been added
                    </p>
                )}
            </div>

            {/* Add Integration Modal */}
            {showModal && selectedType && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-gray-800 rounded-xl shadow-xl w-full max-w-md p-6 border border-gray-700">
                        <div className="flex items-center space-x-3 mb-6">
                            <span className="text-3xl">{selectedType.icon}</span>
                            <div>
                                <h2 className="text-xl font-bold text-white">{selectedType.name}</h2>
                                <p className="text-sm text-gray-400">{selectedType.description}</p>
                            </div>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="space-y-4">
                                {selectedType.fields.map((field) => (
                                    <div key={field.name}>
                                        <label className="block text-sm font-medium text-gray-200 mb-1">
                                            {field.label}
                                        </label>
                                        <input
                                            type={field.type}
                                            className="input w-full"
                                            placeholder={field.placeholder}
                                            value={formData[field.name] || ''}
                                            onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
                                            required
                                        />
                                    </div>
                                ))}
                            </div>
                            <div className="mt-6 flex justify-end space-x-3">
                                <button
                                    type="button"
                                    onClick={() => { setShowModal(false); setSelectedType(null); }}
                                    className="btn btn-secondary"
                                >
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary">
                                    Add Integration
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
