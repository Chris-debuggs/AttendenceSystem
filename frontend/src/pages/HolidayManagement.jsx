import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useToast } from '../context/ToastContext';
import ConfirmationModal from '../components/ConfirmationModal';
import './HolidayManagement.css';

const HolidayManagement = () => {
    const [year, setYear] = useState(new Date().getFullYear());
    const [holidays, setHolidays] = useState([]);
    const [workingDays, setWorkingDays] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [deleteHoliday, setDeleteHoliday] = useState(null);
    const { showSuccess, showError } = useToast();

    const [formData, setFormData] = useState({
        date: new Date().toISOString().split('T')[0],
        name: '',
        description: '',
        type: 'PUBLIC_HOLIDAY',
        is_recurring: false
    });

    const [workingDayForm, setWorkingDayForm] = useState({
        date: '',
        name: '',
        description: ''
    });

    useEffect(() => {
        fetchHolidays();
        fetchWorkingDays();
    }, [year]);

    const fetchHolidays = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`http://localhost:8000/holidays/?year=${year}`);
            setHolidays(response.data || []);
        } catch (error) {
            showError('Failed to fetch holidays');
        } finally {
            setLoading(false);
        }
    };

    const fetchWorkingDays = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/working-days/?year=${year}`);
            setWorkingDays(response.data || []);
        } catch (error) {
            console.error('Failed to fetch working days');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axios.post('http://localhost:8000/holidays/', formData);
            showSuccess('Holiday added successfully');
            setShowForm(false);
            setFormData({
                date: new Date().toISOString().split('T')[0],
                name: '',
                description: '',
                type: 'PUBLIC_HOLIDAY',
                is_recurring: false
            });
            fetchHolidays();
        } catch (error) {
            showError(error.response?.data?.detail || 'Failed to add holiday');
        }
    };

    const handleDelete = async () => {
        try {
            await axios.delete(`http://localhost:8000/holidays/${deleteHoliday.id}`);
            showSuccess('Holiday deleted successfully');
            setDeleteHoliday(null);
            fetchHolidays();
        } catch (error) {
            showError('Failed to delete holiday');
        }
    };

    const addWorkingDay = async (e) => {
        e.preventDefault();
        try {
            await axios.post('http://localhost:8000/working-days/', workingDayForm);
            showSuccess('Weekend converted to working day');
            setWorkingDayForm({ date: '', name: '', description: '' });
            fetchWorkingDays();
        } catch (error) {
            showError(error.response?.data?.detail || 'Failed to add working day');
        }
    };

    const deleteWorkingDay = async (id) => {
        try {
            await axios.delete(`http://localhost:8000/working-days/${id}`);
            showSuccess('Working day removed');
            fetchWorkingDays();
        } catch (error) {
            showError('Failed to remove working day');
        }
    };

    return (
        <div className="holiday-management-page fade-in">
            <div className="page-header">
                <div>
                    <h1>Holiday Management</h1>
                    <p>Manage company holidays and working days</p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowForm(true)}>
                    + Add Holiday
                </button>
            </div>

            <div className="controls-card card">
                <div className="form-group">
                    <label>Year</label>
                    <select value={year} onChange={(e) => setYear(parseInt(e.target.value))}>
                        {[2023, 2024, 2025, 2026].map(y => (
                            <option key={y} value={y}>{y}</option>
                        ))}
                    </select>
                </div>
            </div>

            {showForm && (
                <div className="card mb-3">
                    <h3>Add New Holiday</h3>
                    <form onSubmit={handleSubmit}>
                        <div className="form-row">
                            <div className="form-group">
                                <label>Date *</label>
                                <input
                                    type="date"
                                    value={formData.date}
                                    onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Name *</label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Type *</label>
                                <select
                                    value={formData.type}
                                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                                    required
                                >
                                    <option value="PUBLIC_HOLIDAY">Public Holiday</option>
                                    <option value="COMPANY_HOLIDAY">Company Holiday</option>
                                    <option value="OPTIONAL_HOLIDAY">Optional Holiday</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>
                                    <input
                                        type="checkbox"
                                        checked={formData.is_recurring}
                                        onChange={(e) => setFormData({ ...formData, is_recurring: e.target.checked })}
                                    />
                                    {' '}Recurring yearly
                                </label>
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Description</label>
                            <input
                                type="text"
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            />
                        </div>

                        <div className="form-actions">
                            <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>
                                Cancel
                            </button>
                            <button type="submit" className="btn btn-primary">
                                Add Holiday
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="content-grid">
                <div className="card">
                    <h3>Holidays for {year}</h3>
                    {loading ? (
                        <div className="spinner"></div>
                    ) : holidays.length === 0 ? (
                        <p className="text-muted">No holidays added yet</p>
                    ) : (
                        <div className="holiday-list">
                            {holidays.map(holiday => (
                                <div key={holiday.id} className="holiday-item">
                                    <div>
                                        <div className="holiday-name">{holiday.name}</div>
                                        <div className="holiday-date">{new Date(holiday.date).toLocaleDateString()}</div>
                                        {holiday.description && <div className="text-muted">{holiday.description}</div>}
                                    </div>
                                    <button
                                        className="btn-icon text-error"
                                        onClick={() => setDeleteHoliday(holiday)}
                                    >
                                        🗑️
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="card">
                    <h3>Convert Weekend to Working Day</h3>
                    <form onSubmit={addWorkingDay}>
                        <div className="form-group">
                            <label>Date (Saturday/Sunday) *</label>
                            <input
                                type="date"
                                value={workingDayForm.date}
                                onChange={(e) => setWorkingDayForm({ ...workingDayForm, date: e.target.value })}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Name *</label>
                            <input
                                type="text"
                                value={workingDayForm.name}
                                onChange={(e) => setWorkingDayForm({ ...workingDayForm, name: e.target.value })}
                                placeholder="e.g., Special Working Day"
                                required
                            />
                        </div>
                        <button type="submit" className="btn btn-primary">
                            Convert to Working Day
                        </button>
                    </form>

                    {workingDays.length > 0 && (
                        <div className="working-days-list mt-3">
                            <h4>Working Days ({year})</h4>
                            {workingDays.map(day => (
                                <div key={day.id} className="holiday-item">
                                    <div>
                                        <div className="holiday-name">{day.name}</div>
                                        <div className="holiday-date">{new Date(day.date).toLocaleDateString()}</div>
                                    </div>
                                    <button
                                        className="btn-icon text-error"
                                        onClick={() => deleteWorkingDay(day.id)}
                                    >
                                        🗑️
                                    </button>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {deleteHoliday && (
                <ConfirmationModal
                    message={`Are you sure you want to delete ${deleteHoliday.name}?`}
                    onConfirm={handleDelete}
                    onCancel={() => setDeleteHoliday(null)}
                />
            )}
        </div>
    );
};

export default HolidayManagement;
