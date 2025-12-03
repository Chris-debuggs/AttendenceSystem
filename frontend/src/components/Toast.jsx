import React from 'react';
import { useToast } from '../context/ToastContext';
import './Toast.css';

const Toast = () => {
    const { toasts } = useToast();

    return (
        <div className="toast-container">
            {toasts.map(toast => (
                <div key={toast.id} className={`toast toast-${toast.type}`}>
                    <div className="toast-icon">
                        {toast.type === 'success' && '✓'}
                        {toast.type === 'error' && '✕'}
                        {toast.type === 'info' && 'ℹ'}
                    </div>
                    <div className="toast-message">{toast.message}</div>
                </div>
            ))}
        </div>
    );
};

export default Toast;
