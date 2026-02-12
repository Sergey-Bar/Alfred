import { useEffect, useRef } from 'react';
import {
    ExclamationTriangleIcon,
    TrashIcon,
    QuestionMarkCircleIcon,
    InformationCircleIcon,
} from '@heroicons/react/24/outline';

const DIALOG_TYPES = {
    danger: {
        icon: TrashIcon,
        iconBg: 'bg-red-100 dark:bg-red-900/30',
        iconColor: 'text-red-600 dark:text-red-400',
        confirmBg: 'bg-red-600 hover:bg-red-700',
    },
    warning: {
        icon: ExclamationTriangleIcon,
        iconBg: 'bg-yellow-100 dark:bg-yellow-900/30',
        iconColor: 'text-yellow-600 dark:text-yellow-400',
        confirmBg: 'bg-yellow-600 hover:bg-yellow-700',
    },
    info: {
        icon: InformationCircleIcon,
        iconBg: 'bg-blue-100 dark:bg-blue-900/30',
        iconColor: 'text-blue-600 dark:text-blue-400',
        confirmBg: 'bg-blue-600 hover:bg-blue-700',
    },
    confirm: {
        icon: QuestionMarkCircleIcon,
        iconBg: 'bg-[#1d3557]/10 dark:bg-[#1d3557]/30',
        iconColor: 'text-[#1d3557] dark:text-blue-400',
        confirmBg: 'bg-[#1d3557] hover:bg-[#2d4a6f]',
    },
};

/**
 * ConfirmDialog - A modal confirmation dialog
 * 
 * @param {boolean} isOpen - Whether the dialog is open
 * @param {function} onClose - Called when dialog should close
 * @param {function} onConfirm - Called when user confirms
 * @param {string} title - Dialog title
 * @param {string} message - Dialog message
 * @param {string} confirmText - Text for confirm button (default: "Confirm")
 * @param {string} cancelText - Text for cancel button (default: "Cancel")
 * @param {string} type - Dialog type: 'danger' | 'warning' | 'info' | 'confirm'
 * @param {boolean} loading - Show loading state on confirm button
 */
export default function ConfirmDialog({
    isOpen,
    onClose,
    onConfirm,
    title = 'Confirm Action',
    message = 'Are you sure you want to proceed?',
    confirmText = 'Confirm',
    cancelText = 'Cancel',
    type = 'confirm',
    loading = false,
}) {
    const dialogRef = useRef(null);
    const config = DIALOG_TYPES[type] || DIALOG_TYPES.confirm;
    const Icon = config.icon;

    // Handle escape key
    useEffect(() => {
        const handleEsc = (e) => {
            if (e.key === 'Escape' && isOpen) {
                onClose();
            }
        };
        document.addEventListener('keydown', handleEsc);
        return () => document.removeEventListener('keydown', handleEsc);
    }, [isOpen, onClose]);

    // Focus trap
    useEffect(() => {
        if (isOpen && dialogRef.current) {
            const firstButton = dialogRef.current.querySelector('button');
            firstButton?.focus();
        }
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[60] overflow-y-auto">
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/50 transition-opacity animate-fade-in"
                onClick={onClose}
            />

            {/* Dialog */}
            <div className="flex min-h-full items-center justify-center p-4">
                <div
                    ref={dialogRef}
                    className="relative bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full animate-scale-in"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="dialog-title"
                >
                    <div className="p-6">
                        {/* Icon */}
                        <div className={`mx-auto flex h-12 w-12 items-center justify-center rounded-full ${config.iconBg}`}>
                            <Icon className={`h-6 w-6 ${config.iconColor}`} />
                        </div>

                        {/* Content */}
                        <div className="mt-4 text-center">
                            <h3
                                id="dialog-title"
                                className="text-lg font-semibold text-gray-900 dark:text-white"
                            >
                                {title}
                            </h3>
                            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                                {message}
                            </p>
                        </div>

                        {/* Actions */}
                        <div className="mt-6 flex space-x-3">
                            <button
                                type="button"
                                onClick={onClose}
                                disabled={loading}
                                className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors disabled:opacity-50"
                            >
                                {cancelText}
                            </button>
                            <button
                                type="button"
                                onClick={onConfirm}
                                disabled={loading}
                                className={`flex-1 px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center ${config.confirmBg}`}
                            >
                                {loading ? (
                                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                    </svg>
                                ) : (
                                    confirmText
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
