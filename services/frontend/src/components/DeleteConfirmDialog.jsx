import { AlertTriangle } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

export default function DeleteConfirmDialog({
    isOpen,
    onClose,
    onConfirm,
    itemName,
    itemType = 'item',
    loading = false,
}) {
    const [confirmText, setConfirmText] = useState('');
    const inputRef = useRef(null);

    const isValid = confirmText.trim().toLowerCase() === 'delete';

    // Reset on open/close
    useEffect(() => {
        if (isOpen) {
            setConfirmText('');
            setTimeout(() => inputRef.current?.focus(), 100);
        }
    }, [isOpen]);

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

    const handleSubmit = (e) => {
        e.preventDefault();
        if (isValid && !loading) {
            onConfirm();
        }
    };

    const handleDeleteClick = () => {
        if (isValid && !loading) {
            onConfirm();
        }
    };

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
                    className="relative bg-gray-800 rounded-xl shadow-xl max-w-md w-full animate-scale-in border border-gray-700"
                    role="dialog"
                    aria-modal="true"
                >
                    <div className="p-6">
                        {/* Icon */}
                        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-900/30">
                            <AlertTriangle className="h-6 w-6 text-red-400" />
                        </div>

                        {/* Content */}
                        <div className="mt-4 text-center">
                            <h3 className="text-lg font-semibold text-white">
                                Delete {itemType}?
                            </h3>
                            <p className="mt-2 text-sm text-gray-400">
                                Are you sure you want to delete{' '}
                                <span className="font-semibold text-white">"{itemName}"</span>?
                                This action cannot be undone.
                            </p>
                        </div>

                        {/* Confirmation Input */}
                        <form onSubmit={handleSubmit} className="mt-4">
                            <label className="block text-sm text-gray-400 mb-2 text-center">
                                Type <span className="font-mono font-bold text-red-400">delete</span> to confirm
                            </label>
                            <input
                                ref={inputRef}
                                type="text"
                                value={confirmText}
                                onChange={(e) => setConfirmText(e.target.value)}
                                placeholder="Type 'delete' here..."
                                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent text-center"
                                disabled={loading}
                                autoComplete="off"
                            />

                            {/* Actions */}
                            <div className="mt-6 flex space-x-3">
                                <button
                                    type="button"
                                    onClick={onClose}
                                    disabled={loading}
                                    className="flex-1 px-4 py-2 text-sm font-medium text-gray-200 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors disabled:opacity-50"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    onClick={handleDeleteClick}
                                    disabled={!isValid || loading}
                                    className="flex-1 px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                                >
                                    {loading ? (
                                        <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                        </svg>
                                    ) : (
                                        'Delete'
                                    )}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}
