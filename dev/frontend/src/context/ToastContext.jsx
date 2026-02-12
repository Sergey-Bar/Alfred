import {
    CheckCircleIcon,
    ExclamationTriangleIcon,
    InformationCircleIcon,
    XCircleIcon,
    XMarkIcon,
} from '@heroicons/react/24/outline';
import { createContext, useCallback, useContext, useState } from 'react';

const ToastContext = createContext(null);

const TOAST_TYPES = {
    success: {
        icon: CheckCircleIcon,
        bgColor: 'bg-green-900/30',
        borderColor: 'border-green-800',
        iconColor: 'text-green-400',
        textColor: 'text-green-200',
    },
    error: {
        icon: XCircleIcon,
        bgColor: 'bg-red-900/30',
        borderColor: 'border-red-800',
        iconColor: 'text-red-400',
        textColor: 'text-red-200',
    },
    warning: {
        icon: ExclamationTriangleIcon,
        bgColor: 'bg-yellow-900/30',
        borderColor: 'border-yellow-800',
        iconColor: 'text-yellow-400',
        textColor: 'text-yellow-200',
    },
    info: {
        icon: InformationCircleIcon,
        bgColor: 'bg-blue-900/30',
        borderColor: 'border-blue-800',
        iconColor: 'text-blue-400',
        textColor: 'text-blue-200',
    },
};

function Toast({ id, type, title, message, onClose }) {
    const config = TOAST_TYPES[type] || TOAST_TYPES.info;
    const Icon = config.icon;

    return (
        <div
            className={`
                flex items-start p-4 rounded-lg border shadow-lg animate-slide-in
                ${config.bgColor} ${config.borderColor}
            `}
            role="alert"
        >
            <Icon className={`h-5 w-5 flex-shrink-0 ${config.iconColor}`} />
            <div className="ml-3 flex-1">
                {title && (
                    <p className={`text-sm font-medium ${config.textColor}`}>{title}</p>
                )}
                {message && (
                    <p className={`text-sm mt-1 ${config.textColor} opacity-90`}>{message}</p>
                )}
            </div>
            <button
                onClick={() => onClose(id)}
                className={`ml-4 flex-shrink-0 p-0.5 rounded hover:bg-white/10 transition-colors ${config.iconColor}`}
            >
                <XMarkIcon className="h-4 w-4" />
            </button>
        </div>
    );
}

export function ToastProvider({ children }) {
    const [toasts, setToasts] = useState([]);

    const removeToast = useCallback((id) => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
    }, []);

    const addToast = useCallback(({ type = 'info', title, message, duration = 5000 }) => {
        const id = Date.now() + Math.random();

        setToasts(prev => [...prev, { id, type, title, message }]);

        if (duration > 0) {
            setTimeout(() => {
                setToasts(prev => prev.filter(toast => toast.id !== id));
            }, duration);
        }

        return id;
    }, []);

    const success = useCallback((title, message) => {
        return addToast({ type: 'success', title, message });
    }, [addToast]);

    const error = useCallback((title, message) => {
        return addToast({ type: 'error', title, message });
    }, [addToast]);

    const warning = useCallback((title, message) => {
        return addToast({ type: 'warning', title, message });
    }, [addToast]);

    const info = useCallback((title, message) => {
        return addToast({ type: 'info', title, message });
    }, [addToast]);

    return (
        <ToastContext.Provider value={{ addToast, removeToast, success, error, warning, info }}>
            {children}

            {/* Toast Container */}
            <div className="fixed top-4 right-4 z-[100] flex flex-col space-y-2 max-w-sm w-full pointer-events-none">
                {toasts.map(toast => (
                    <div key={toast.id} className="pointer-events-auto">
                        <Toast
                            {...toast}
                            onClose={removeToast}
                        />
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    );
}

export function useToast() {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within a ToastProvider');
    }
    return context;
}
