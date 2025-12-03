import React, { useState } from 'react';
import axios from 'axios';
import { useToast } from '../context/ToastContext';

const PunchOutModal = ({ employeeName, onClose, onSuccess }) => {
    const [loading, setLoading] = useState(false);
    const { showSuccess, showError } = useToast();

    const handlePunchOut = async () => {
        setLoading(true);
        try {
            const response = await axios.post('http://localhost:8000/punch_out', {
                name: employeeName
            });
            if (response.data.status === 'success') {
                showSuccess(response.data.message);
                onSuccess();
                onClose();
            }
        } catch (error) {
            showError(error.response?.data?.detail || 'Failed to punch out');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>Punch Out</h3>
                </div>
                <p className="modal-message">
                    Do you want to punch out <strong>{employeeName}</strong>?
                </p>
                <div className="modal-footer">
                    <button className="btn btn-secondary" onClick={onClose} disabled={loading}>
                        Cancel
                    </button>
                    <button className="btn btn-primary" onClick={handlePunchOut} disabled={loading}>
                        {loading ? 'Processing...' : 'Punch Out'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default PunchOutModal;
