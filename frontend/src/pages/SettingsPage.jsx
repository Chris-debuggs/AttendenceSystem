import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useToast } from '../context/ToastContext';
import './SettingsPage.css';

const SettingsPage = () => {
    const [officeSettings, setOfficeSettings] = useState(null);
    const [loading, setLoading] = useState(true);
    const { showSuccess, showError } = useToast();

    const [officeForm, setOfficeForm] = useState({
        start_time: '',
        end_time: '',
        on_time_limit: ''
    });

    const [credentialsForm, setCredentialsForm] = useState({
        current_username: '',
        current_password: '',
        new_username: '',
        new_password: ''
    });

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        setLoading(true);
        try {
            const response = await axios.get('http://localhost:8000/office-settings');
            setOfficeSettings(response.data);
            setOfficeForm({
                start_time: response.data.start_time,
                end_time: response.data.end_time,
                on_time_limit: response.data.on_time_limit
            });
        } catch (error) {
            showError('Failed to fetch settings');
        } finally {
            setLoading(false);
        }
    };

    const handleOfficeUpdate = async (e) => {
        e.preventDefault();
        try {
            await axios.put('http://localhost:8000/office-settings', officeForm);
            showSuccess('Office settings updated successfully');
            fetchSettings();
        } catch (error) {
            showError(error.response?.data?.detail || 'Failed to update settings');
        }
    };

    const handleCredentialsUpdate = async (e) => {
        e.preventDefault();
        try {
            await axios.put('http://localhost:8000/admin/credentials', credentialsForm);
            showSuccess('Credentials updated successfully. Please login again.');
            setCredentialsForm({
                current_username: '',
                current_password: '',
                new_username: '',
                new_password: ''
            });

            // Logout after credential change
            setTimeout(() => {
                localStorage.removeItem('isAuthenticated');
                localStorage.removeItem('adminUser');
                window.location.href = '/login';
            }, 2000);
        } catch (error) {
            showError(error.response?.data?.detail || 'Failed to update credentials');
        }
    };

    return (
        <div className="settings-page fade-in">
            <div className="page-header">
                <div>
                    <h1>Settings</h1>
                    <p>Configure system settings</p>
                </div>
            </div>

            {loading ? (
                <div className="flex justify-center">
                    <div className="spinner"></div>
                </div>
            ) : (
                <div className="settings-grid">
                    <div className="card">
                        <h3>Office Hours Settings</h3>
                        <form onSubmit={handleOfficeUpdate}>
                            <div className="form-group">
                                <label>Office Start Time *</label>
                                <input
                                    type="time"
                                    value={officeForm.start_time}
                                    onChange={(e) => setOfficeForm({ ...officeForm, start_time: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Office End Time *</label>
                                <input
                                    type="time"
                                    value={officeForm.end_time}
                                    onChange={(e) => setOfficeForm({ ...officeForm, end_time: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>On-Time Limit (minutes) *</label>
                                <input
                                    type="number"
                                    value={officeForm.on_time_limit}
                                    onChange={(e) => setOfficeForm({ ...officeForm, on_time_limit: e.target.value })}
                                    required
                                    placeholder="e.g., 15"
                                />
                                <small className="text-muted">Employees arriving within this time are marked as on-time</small>
                            </div>
                            <button type="submit" className="btn btn-primary">
                                Update Office Settings
                            </button>
                        </form>
                    </div>

                    <div className="card">
                        <h3>Admin Credentials</h3>
                        <form onSubmit={handleCredentialsUpdate}>
                            <div className="form-group">
                                <label>Current Username *</label>
                                <input
                                    type="text"
                                    value={credentialsForm.current_username}
                                    onChange={(e) => setCredentialsForm({ ...credentialsForm, current_username: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Current Password *</label>
                                <input
                                    type="password"
                                    value={credentialsForm.current_password}
                                    onChange={(e) => setCredentialsForm({ ...credentialsForm, current_password: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>New Username (optional)</label>
                                <input
                                    type="text"
                                    value={credentialsForm.new_username}
                                    onChange={(e) => setCredentialsForm({ ...credentialsForm, new_username: e.target.value })}
                                    placeholder="Leave blank to keep current"
                                />
                            </div>
                            <div className="form-group">
                                <label>New Password (optional)</label>
                                <input
                                    type="password"
                                    value={credentialsForm.new_password}
                                    onChange={(e) => setCredentialsForm({ ...credentialsForm, new_password: e.target.value })}
                                    placeholder="Leave blank to keep current"
                                />
                            </div>
                            <button type="submit" className="btn btn-primary">
                                Update Credentials
                            </button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SettingsPage;
