import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useToast } from '../context/ToastContext';
import ConfirmationModal from '../components/ConfirmationModal';
import CaptureModal from '../components/CaptureModal';
import './AddRemoveEmployeePage.css';

const AddRemoveEmployeePage = () => {
    const [employees, setEmployees] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingEmployee, setEditingEmployee] = useState(null);
    const [deleteEmployee, setDeleteEmployee] = useState(null);
    const [captureEmployee, setCaptureEmployee] = useState(null);
    const { showSuccess, showError } = useToast();

    const [formData, setFormData] = useState({
        id: '',
        name: '',
        email: '',
        mobile_no: '',
        address: '',
        gender: 'Male',
        department: '',
        position: '',
        salary: '',
        working_hours_per_day: '8',
        employee_type: 'Full-time',
        joining_date: new Date().toISOString().split('T')[0]
    });

    useEffect(() => {
        fetchEmployees();
    }, []);

    const fetchEmployees = async () => {
        try {
            const response = await axios.get('http://localhost:8000/employees/');
            setEmployees(response.data.employees || []);
        } catch (error) {
            showError('Failed to fetch employees');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const data = {
                ...formData,
                salary: parseFloat(formData.salary) || 0,
                working_hours_per_day: parseFloat(formData.working_hours_per_day) || 8
            };

            if (editingEmployee) {
                await axios.put(`http://localhost:8000/employees/${editingEmployee.id}`, data);
                showSuccess('Employee updated successfully');
            } else {
                await axios.post('http://localhost:8000/employees/', data);
                showSuccess('Employee added successfully');
            }

            resetForm();
            fetchEmployees();
        } catch (error) {
            showError(error.response?.data?.message || 'Failed to save employee');
        }
    };

    const handleDelete = async () => {
        try {
            await axios.delete(`http://localhost:8000/employees/${deleteEmployee.id}`);
            showSuccess('Employee deleted successfully');
            setDeleteEmployee(null);
            fetchEmployees();
        } catch (error) {
            showError('Failed to delete employee');
        }
    };

    const handleEdit = (employee) => {
        setEditingEmployee(employee);
        setFormData(employee);
        setShowForm(true);
    };

    const resetForm = () => {
        setFormData({
            id: '',
            name: '',
            email: '',
            mobile_no: '',
            address: '',
            gender: 'Male',
            department: '',
            position: '',
            salary: '',
            working_hours_per_day: '8',
            employee_type: 'Full-time',
            joining_date: new Date().toISOString().split('T')[0]
        });
        setEditingEmployee(null);
        setShowForm(false);
    };

    return (
        <div className="employee-page fade-in">
            <div className="page-header">
                <div>
                    <h1>Employee Management</h1>
                    <p>Manage your team members</p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowForm(true)}>
                    + Add Employee
                </button>
            </div>

            {showForm && (
                <div className="card mb-3">
                    <h3>{editingEmployee ? 'Edit Employee' : 'Add New Employee'}</h3>
                    <form onSubmit={handleSubmit}>
                        <div className="form-row">
                            <div className="form-group">
                                <label>Employee ID *</label>
                                <input
                                    type="text"
                                    value={formData.id}
                                    onChange={(e) => setFormData({ ...formData, id: e.target.value })}
                                    required
                                    disabled={!!editingEmployee}
                                />
                            </div>
                            <div className="form-group">
                                <label>Full Name *</label>
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
                                <label>Email *</label>
                                <input
                                    type="email"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Mobile Number *</label>
                                <input
                                    type="tel"
                                    value={formData.mobile_no}
                                    onChange={(e) => setFormData({ ...formData, mobile_no: e.target.value })}
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Address</label>
                            <input
                                type="text"
                                value={formData.address}
                                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                            />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Gender *</label>
                                <select
                                    value={formData.gender}
                                    onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                                    required
                                >
                                    <option value="Male">Male</option>
                                    <option value="Female">Female</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>Department *</label>
                                <input
                                    type="text"
                                    value={formData.department}
                                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Position *</label>
                                <input
                                    type="text"
                                    value={formData.position}
                                    onChange={(e) => setFormData({ ...formData, position: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label>Employee Type *</label>
                                <select
                                    value={formData.employee_type}
                                    onChange={(e) => setFormData({ ...formData, employee_type: e.target.value })}
                                    required
                                >
                                    <option value="Full-time">Full-time</option>
                                    <option value="Part-time">Part-time</option>
                                    <option value="Contract">Contract</option>
                                    <option value="Intern">Intern</option>
                                </select>
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Salary</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={formData.salary}
                                    onChange={(e) => setFormData({ ...formData, salary: e.target.value })}
                                />
                            </div>
                            <div className="form-group">
                                <label>Working Hours/Day</label>
                                <input
                                    type="number"
                                    step="0.5"
                                    value={formData.working_hours_per_day}
                                    onChange={(e) => setFormData({ ...formData, working_hours_per_day: e.target.value })}
                                />
                            </div>
                            <div className="form-group">
                                <label>Joining Date *</label>
                                <input
                                    type="date"
                                    value={formData.joining_date}
                                    onChange={(e) => setFormData({ ...formData, joining_date: e.target.value })}
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-actions">
                            <button type="button" className="btn btn-secondary" onClick={resetForm}>
                                Cancel
                            </button>
                            <button type="submit" className="btn btn-primary">
                                {editingEmployee ? 'Update Employee' : 'Add Employee'}
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
                                <th>ID</th>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Mobile</th>
                                <th>Department</th>
                                <th>Position</th>
                                <th>Photo</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {employees.map((emp) => (
                                <tr key={emp.id}>
                                    <td>{emp.id}</td>
                                    <td>{emp.name}</td>
                                    <td>{emp.email}</td>
                                    <td>{emp.mobile_no}</td>
                                    <td>{emp.department}</td>
                                    <td>{emp.position}</td>
                                    <td>
                                        {emp.has_photo ? (
                                            <span className="badge badge-success">✓</span>
                                        ) : (
                                            <span className="badge badge-warning">✗</span>
                                        )}
                                    </td>
                                    <td>
                                        <div className="action-buttons">
                                            <button
                                                className="btn-icon"
                                                onClick={() => setCaptureEmployee(emp)}
                                                title="Upload Photo"
                                            >
                                                📷
                                            </button>
                                            <button
                                                className="btn-icon"
                                                onClick={() => handleEdit(emp)}
                                                title="Edit"
                                            >
                                                ✏️
                                            </button>
                                            <button
                                                className="btn-icon text-error"
                                                onClick={() => setDeleteEmployee(emp)}
                                                title="Delete"
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {deleteEmployee && (
                <ConfirmationModal
                    message={`Are you sure you want to delete ${deleteEmployee.name}?`}
                    onConfirm={handleDelete}
                    onCancel={() => setDeleteEmployee(null)}
                />
            )}

            {captureEmployee && (
                <CaptureModal
                    employeeId={captureEmployee.id}
                    onClose={() => setCaptureEmployee(null)}
                    onSuccess={fetchEmployees}
                />
            )}
        </div>
    );
};

export default AddRemoveEmployeePage;
