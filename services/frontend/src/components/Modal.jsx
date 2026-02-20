/*
──────────────────────────────────────────────────────────────
Model:       Claude Opus 4
Tier:        L2
Logic:       Accessible Modal component with focus trapping, ESC-to-close,
             aria attributes, and backdrop click handling.
Root Cause:  IMP-003 - Inline modals lacked accessibility features.
Context:     Provides consistent accessibility across all modal dialogs.
Suitability: L2 - UI component with accessibility patterns.
──────────────────────────────────────────────────────────────
*/
import { X } from 'lucide-react';
import { useCallback, useEffect, useRef } from 'react';

/**
 * Accessible Modal component with focus trapping
 * 
 * @param {boolean} isOpen - Whether the modal is visible
 * @param {function} onClose - Called when modal should close
 * @param {string} title - Modal title (used for aria-labelledby)
 * @param {React.ReactNode} children - Modal content
 * @param {string} className - Additional classes for the modal container
 * @param {boolean} showCloseButton - Whether to show the X close button
 * @param {string} size - Modal size: 'sm', 'md', 'lg', 'xl', 'full'
 */
export default function Modal({
    isOpen,
    onClose,
    title,
    children,
    className = '',
    showCloseButton = true,
    size = 'md',
}) {
    const modalRef = useRef(null);
    const previousActiveElement = useRef(null);

    // Size classes
    const sizeClasses = {
        sm: 'max-w-sm',
        md: 'max-w-md',
        lg: 'max-w-lg',
        xl: 'max-w-xl',
        '2xl': 'max-w-2xl',
        full: 'max-w-full mx-4',
    };

    // Store previously focused element and restore on close
    useEffect(() => {
        if (isOpen) {
            previousActiveElement.current = document.activeElement;
        } else if (previousActiveElement.current) {
            previousActiveElement.current.focus();
        }
    }, [isOpen]);

    // Focus trap: get all focusable elements
    const getFocusableElements = useCallback(() => {
        if (!modalRef.current) return [];
        return modalRef.current.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
    }, []);

    // Handle ESC key and Tab trapping
    useEffect(() => {
        if (!isOpen) return;

        const handleKeyDown = (e) => {
            // ESC to close
            if (e.key === 'Escape') {
                e.preventDefault();
                onClose();
                return;
            }

            // Tab trapping
            if (e.key === 'Tab') {
                const focusable = getFocusableElements();
                if (focusable.length === 0) return;

                const firstEl = focusable[0];
                const lastEl = focusable[focusable.length - 1];

                if (e.shiftKey) {
                    // Shift + Tab: if on first element, wrap to last
                    if (document.activeElement === firstEl) {
                        e.preventDefault();
                        lastEl.focus();
                    }
                } else {
                    // Tab: if on last element, wrap to first
                    if (document.activeElement === lastEl) {
                        e.preventDefault();
                        firstEl.focus();
                    }
                }
            }
        };

        document.addEventListener('keydown', handleKeyDown);
        return () => document.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, onClose, getFocusableElements]);

    // Focus first focusable element on open
    useEffect(() => {
        if (!isOpen) return;

        // Small delay to ensure modal is rendered
        const timer = setTimeout(() => {
            const focusable = getFocusableElements();
            if (focusable.length > 0) {
                focusable[0].focus();
            }
        }, 50);

        return () => clearTimeout(timer);
    }, [isOpen, getFocusableElements]);

    // Prevent body scroll when modal is open
    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
        return () => {
            document.body.style.overflow = '';
        };
    }, [isOpen]);

    if (!isOpen) return null;

    const titleId = `modal-title-${Math.random().toString(36).substr(2, 9)}`;

    return (
        <div 
            className="fixed inset-0 z-50 overflow-y-auto"
            aria-labelledby={title ? titleId : undefined}
            aria-modal="true"
            role="dialog"
        >
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/50 transition-opacity animate-fade-in"
                onClick={onClose}
                aria-hidden="true"
            />

            {/* Modal container */}
            <div className="flex min-h-full items-center justify-center p-4">
                <div
                    ref={modalRef}
                    className={`
                        relative bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full
                        animate-scale-in border border-gray-200 dark:border-gray-700
                        ${sizeClasses[size] || sizeClasses.md}
                        ${className}
                    `}
                >
                    {/* Header with title and close button */}
                    {(title || showCloseButton) && (
                        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                            {title && (
                                <h2
                                    id={titleId}
                                    className="text-lg font-semibold text-gray-900 dark:text-white"
                                >
                                    {title}
                                </h2>
                            )}
                            {showCloseButton && (
                                <button
                                    type="button"
                                    onClick={onClose}
                                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 
                                               focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg p-1"
                                    aria-label="Close modal"
                                >
                                    <X className="h-5 w-5" />
                                </button>
                            )}
                        </div>
                    )}

                    {/* Content */}
                    <div className="p-4">
                        {children}
                    </div>
                </div>
            </div>
        </div>
    );
}
