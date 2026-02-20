import { useState } from 'react';

const steps = [
    {
        title: 'Welcome to Alfred Admin!',
        description: 'This quick onboarding will walk you through the key admin features: user/team management, quota controls, analytics, and more.'
    },
    {
        title: 'Manage Users & Teams',
        description: 'Add, edit, or remove users and teams. Set quotas, assign roles, and manage access from the Users and Teams pages.'
    },
    {
        title: 'Credit Governance',
        description: 'Allocate, reallocate, and monitor credit usage. Use the Transfers page for dynamic quota management and the Dashboard for real-time analytics.'
    },
    {
        title: 'Audit & Compliance',
        description: 'Track all admin actions in the Activity Log. Ensure compliance with audit trails and permission controls.'
    },
    {
        title: 'Integrations & Notifications',
        description: 'Connect Slack, Teams, and more for alerts. Configure integrations in the Integrations page.'
    },
    {
        title: 'Need Help?',
        description: 'Access the User Guide anytime from the sidebar, or contact support via the Help section.'
    }
];

export default function AdminOnboardingModal({ open, onClose }) {
    const [step, setStep] = useState(0);
    if (!open) return null;
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40">
            <div className="bg-white dark:bg-gray-900 rounded-lg shadow-lg max-w-md w-full p-6 relative">
                <button
                    className="absolute top-2 right-2 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
                    onClick={onClose}
                    aria-label="Close onboarding"
                >
                    ×
                </button>
                <h2 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">{steps[step].title}</h2>
                <p className="text-gray-700 dark:text-gray-300 mb-4">{steps[step].description}</p>
                <div className="flex justify-between items-center mt-6">
                    <button
                        className="px-4 py-2 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200"
                        onClick={() => setStep((s) => Math.max(0, s - 1))}
                        disabled={step === 0}
                    >
                        Back
                    </button>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                        Step {step + 1} of {steps.length}
                    </div>
                    {step < steps.length - 1 ? (
                        <button
                            className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
                            onClick={() => setStep((s) => Math.min(steps.length - 1, s + 1))}
                        >
                            Next
                        </button>
                    ) : (
                        <button
                            className="px-4 py-2 rounded bg-green-600 text-white hover:bg-green-700"
                            onClick={onClose}
                        >
                            Finish
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}
