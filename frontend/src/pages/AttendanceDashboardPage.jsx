import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useToast } from '../context/ToastContext';
import './AttendanceDashboardPage.css';

const AttendanceDashboardPage = () => {
    const [year, setYear] = useState(new Date().getFullYear());
    const [month, setMonth] = useState(new Date().getMonth() + 1);
    const [attendanceData, setAttendanceData] = useState(null);
    const [loading, setLoading] = useState(true);
    const { showSuccess, showError } = useToast();

    useEffect(() => {
        fetchAttendance();
    }, [year, month]);

    const fetchAttendance = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`http://localhost:8000/attendance/${year}/${month}`);
            setAttendanceData(response.data);
        } catch (error) {
            showError('Failed to fetch attendance data');
        } finally {
            setLoading(false);
        }
    };

    const exportCSV = async () => {
        try {
            const response = await axios.post(
                'http://localhost:8000/api/export-attendance-csv',
                {
                    year,
                    month,
                    layout: 'employees-as-columns',
                    fields: { name: true, id: true, department: false, type: false, status: true }
                },
                { responseType: 'blob' }
            );

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `attendance_${year}_${month}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
            showSuccess('CSV exported successfully');
        } catch (error) {
            showError('Failed to export CSV');
        }
    };

    const getStatusClass = (status) => {
        if (!status) return 'status-absent';
        if (status === 'H') return 'status-holiday';
        if (status === 'L') return 'status-leave';
        if (status === 'On Time') return 'status-present';
        if (status === 'Late') return 'status-late';
        return 'status-absent';
    };

    const getStatusLabel = (status) => {
        if (!status) return 'A';
        if (status === 'H') return 'H';
        if (status === 'L') return 'L';
        if (status === 'On Time') return 'P';
        if (status === 'Late') return 'LT';
        return 'A';
    };

    const renderCalendar = () => {
        if (!attendanceData) return null;

        const { attendance, employee_data, daysInMonth, holidays, weekend_days, working_days } = attendanceData;
        const employeeNames = Object.keys(employee_data);
        const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);

        return (
            <div className="calendar-wrapper">
                <table className="attendance-table">
                    <thead>
                        <tr>
                            <th className="sticky-col">Employee</th>
                            {days.map(day => {
                                const isWeekend = weekend_days.includes(day) && !working_days.includes(day);
                                const isHoliday = holidays[day];
                                return (
                                    <th key={day} className={isWeekend ? 'weekend-col' : isHoliday ? 'holiday-col' : ''}>
                                        {day}
                                    </th>
                                );
                            })}
                        </tr>
                    </thead>
                    <tbody>
                        {employeeNames.map(name => (
                            <tr key={name}>
                                <td className="sticky-col employee-name">{name}</td>
                                {days.map(day => {
                                    const dayData = attendance[name]?.[day];
                                    const status = dayData?.status;
                                    return (
                                        <td key={day} className={getStatusClass(status)} title={dayData?.punch_in || status}>
                                            {getStatusLabel(status)}
                                        </td>
                                    );
                                })}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        );
    };

    return (
        <div className="attendance-dashboard-page fade-in">
            <div className="page-header">
                <div>
                    <h1>Attendance Dashboard</h1>
                    <p>Monthly attendance tracking</p>
                </div>
                <button className="btn btn-primary" onClick={exportCSV}>
                    📥 Export CSV
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

            <div className="legend card">
                <h4>Legend</h4>
                <div className="legend-items">
                    <span className="legend-item"><span className="status-present">P</span> Present</span>
                    <span className="legend-item"><span className="status-late">LT</span> Late</span>
                    <span className="legend-item"><span className="status-absent">A</span> Absent</span>
                    <span className="legend-item"><span className="status-leave">L</span> Leave</span>
                    <span className="legend-item"><span className="status-holiday">H</span> Holiday</span>
                </div>
            </div>

            {loading ? (
                <div className="flex justify-center mt-3">
                    <div className="spinner"></div>
                </div>
            ) : (
                renderCalendar()
            )}
        </div>
    );
};

export default AttendanceDashboardPage;
