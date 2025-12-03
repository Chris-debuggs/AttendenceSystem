import React, { createContext, useContext, useState, useCallback } from 'react';

const ToastContext = createContext();

export const useToast = () => {
    const context = useContext(ToastContext);
    if (!context) {
        throw new Error('useToast must be used within ToastProvider');
    }
    return context;
};

export const ToastProvider = ({ children }) => {
    const [toasts, setToasts] = useState([]);

    const showToast = useCallback((message, type = 'info') => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type }]);
        setTimeout(() => {
            setToasts(prev => prev.filter(toast => toast.id !== id));
        }, 3000);
    }, []);

    const showSuccess = useCallback((message) => showToast(message, 'success'), [showToast]);
    const showError = useCallback((message) => showToast(message, 'error'), [showToast]);
    const showInfo = useCallback((message) => showToast(message, 'info'), [showToast]);

    return (
        <ToastContext.Provider value={{ showSuccess, showError, showInfo, toasts }}>
            {children}
        </ToastContext.Provider>
    );
};
