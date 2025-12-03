import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useToast } from '../context/ToastContext';
import ConfirmationModal from '../components/ConfirmationModal';
import './LeaveManagement.css';

const LeaveManagement = () => {
    const [year, setYear] = useState(new Date().getFullYear());
    const [month, setMonth] = useState(new Date().getMonth() + 1);
    const [leaves, setLeaves] = useState([]);
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [deleteLeave, setDeleteLeave] = useState(null);
    const { showSuccess, showError } = useToast();

    const [formData, setFormData] = useState({
        employee_id: '',
        leave_date: new Date().toISOString().split('T')[0],
        leave_type: 'SICK_LEAVE',
        reason: '',
        status: 'approved'
    });

    useEffect(() => {
        fetchEmployees();
        fetchLeaves();
    }, [year, month]);

    const fetchEmployees = async () => {
        try {
            const response = await axios.get('http://localhost:8000/employees/');
            setEmployees(response.data.employees || []);
        } catch (error) {
            console.error('Failed to fetch employees');
        }
    };

    const fetchLeaves = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`http://localhost:8000/leaves/?year=${year}&month=${month}`);
            setLeaves(response.data || []);
        } catch (error) {
            showError('Failed to fetch leaves');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axios.post('http://localhost:8000/leaves/', formData);
            showSuccess('Leave added successfully');
            setShowForm(false);
            setFormData({
                employee_id: '',
                leave_date: new Date().toISOString().split('T')[0],
                leave_type: 'SICK_LEAVE',
                reason: '',
                status: 'approved'
            });
            fetchLeaves();
        } catch (error) {
            showError(error.response?.data?.detail || 'Failed to add leave');
        }
    };

    const handleDelete = async () => {
        try {
            await axios.delete(`http://localhost:8000/leaves/${deleteLeave.id}`);
            showSuccess('Leave deleted successfully');
            setDeleteLeave(null);
            fetchLeaves();
        } catch (error) {
            showError('Failed to delete leave');
        }
    };

    const getEmployeeName = (employeeId) => {
        const emp = employees.find(e => e.id === employeeId);
        return emp ? emp.name : employeeId;
    };

    return (
        <div className="leave-management-page fade-in">
            <div className="page-header">
                <div>
                    <h1>Leave Management</h1>
                    <p>Manage employee leaves</p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowForm(true)}>
                    + Add Leave
                </button>
            </div>

            <div className="controls-card card">
                <div className="controls-grid">
                    <div className="form-group">
                        <label>Year</label>
                        <select value={year} onChange={(e) => setYear(parseInt(e.target.value))}>
                            {[2023, 2024, 2025, 2026].map(y => (
                                <option key={y} value={y}>{y}</option>
                            ))}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Month</label>
                        <select value={month} onChange={(e) => setMonth(parseInt(e.target.value))}>
                            {Array.from({ length: 12 }, (_, i) => (
                                <option key={i + 1} value={i + 1}>
                                    {new Date(2000, i, 1).toLocaleString('default', { month: 'long' })}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {showForm && (
                <div className="card mb-3">
                    <h3>Add New Leave</h3>
                    <form onSubmit={handleSubmit}>
                        <div className="form-row">
                            <div className="form-group">
                                <label>Employee *</label>
                                <select
                                    value={formData.employee_id}
                                    onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                                    required
                                >
                                    <option value="">Select Employee</option>
                                    {employees.map(emp => (
                                        <option key={emp.id} value={emp.id}>{emp.name}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Leave Date *</label>
                                <input
                                    type="date"
                                    value={formData.leave_date}
                                    onChange={(e) => setFormData({ ...formData, leave_date: e.target.value })}
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Leave Type *</label>
                                <select
                                    value={formData.leave_type}
                                    onChange={(e) => setFormData({ ...formData, leave_type: e.target.value })}
                                    required
                                >
                                    <option value="SICK_LEAVE">Sick Leave</option>
                                    <option value="CASUAL_LEAVE">Casual Leave</option>
                                    <option value="EARNED_LEAVE">Earned Leave</option>
                                    <option value="UNPAID_LEAVE">Unpaid Leave</option>
                                    <option value="MATERNITY_LEAVE">Maternity Leave</option>
                                    <option value="PATERNITY_LEAVE">Paternity Leave</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Status *</label>
                                <select
                                    value={formData.status}
                                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                                    required
                                >
                                    <option value="approved">Approved</option>
                                    <option value="pending">Pending</option>
                                    <option value="rejected">Rejected</option>
                                </select>
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Reason</label>
                            <input
                                type="text"
                                value={formData.reason}
                                onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                                placeholder="Optional reason"
                            />
                        </div>

                        <div className="form-actions">
                            <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>
                                Cancel
                            </button>
                            <button type="submit" className="btn btn-primary">
                                Add Leave
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {loading ? (
                <div className="flex justify-center">
                    <div className="spinner"></div>
                </div>
            ) : (
                <div className="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Employee</th>
                                <th>Leave Date</th>
                                <th>Leave Type</th>
                                <th>Reason</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {leaves.length === 0 ? (
                                <tr>
                                    <td colSpan="6" style={{ textAlign: 'center' }}>
                                        <p className="text-muted">No leaves found for this period</p>
                                    </td>
                                </tr>
                            ) : (
                                leaves.map((leave) => (
                                    <tr key={leave.id}>
                                        <td>{getEmployeeName(leave.employee_id)}</td>
                                        <td>{new Date(leave.leave_date).toLocaleDateString()}</td>
                                        <td>{leave.leave_type.replace(/_/g, ' ')}</td>
                                        <td>{leave.reason || '-'}</td>
                                        <td>
                                            <span className={`badge badge-${leave.status === 'approved' ? 'success' : leave.status === 'rejected' ? 'error' : 'warning'}`}>
                                                {leave.status}
                                            </span>
                                        </td>
                                        <td>
                                            <button
                                                className="btn-icon text-error"
                                                onClick={() => setDeleteLeave(leave)}
                                                title="Delete"
                                            >
                                                🗑️
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            )}

            {deleteLeave && (
                <ConfirmationModal
                    message={`Are you sure you want to delete this leave?`}
                    onConfirm={handleDelete}
                    onCancel={() => setDeleteLeave(null)}
                />
            )}
        </div>
    );
};

export default LeaveManagement;
