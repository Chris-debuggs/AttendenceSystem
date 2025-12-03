import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useToast } from '../context/ToastContext';
import './PayrollPage.css';

const PayrollPage = () => {
    const [year, setYear] = useState(new Date().getFullYear());
    const [month, setMonth] = useState(new Date().getMonth() + 1);
    const [employees, setEmployees] = useState([]);
    const [attendanceData, setAttendanceData] = useState(null);
    const [loading, setLoading] = useState(true);
    const { showError } = useToast();

    useEffect(() => {
        fetchData();
    }, [year, month]);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [empResponse, attResponse] = await Promise.all([
                axios.get('http://localhost:8000/employees/'),
                axios.get(`http://localhost:8000/attendance/${year}/${month}`)
            ]);

            setEmployees(empResponse.data.employees || []);
            setAttendanceData(attResponse.data);
        } catch (error) {
            showError('Failed to fetch payroll data');
        } finally {
            setLoading(false);
        }
    };

    const calculatePayroll = (employee) => {
        if (!attendanceData || !employee.salary) return null;

        const empAttendance = attendanceData.attendance[employee.name] || {};
        const totalDays = attendanceData.daysInMonth;
        const weekendDays = attendanceData.weekend_days.filter(d => !attendanceData.working_days.includes(d));
        const holidays = Object.keys(attendanceData.holidays).length;

        // Calculate actual working days in month
        const workingDaysInMonth = totalDays - weekendDays.length;

        // Count present days
        let presentDays = 0;
        for (let day = 1; day <= totalDays; day++) {
            const status = empAttendance[day]?.status;
            if (status === 'On Time' || status === 'Late' || status === 'L') {
                presentDays++;
            }
        }

        const perDaySalary = employee.salary / workingDaysInMonth;
        const earnedSalary = presentDays * perDaySalary;
        const deduction = employee.salary - earnedSalary;

        return {
            totalDays,
            workingDays: workingDaysInMonth,
            presentDays,
            weekendDays: weekendDays.length,
            holidays,
            baseSalary: employee.salary,
            perDaySalary: perDaySalary.toFixed(2),
            earnedSalary: earnedSalary.toFixed(2),
            deduction: deduction.toFixed(2)
        };
    };

    return (
        <div className="payroll-page fade-in">
            <div className="page-header">
                <div>
                    <h1>Payroll Management</h1>
                    <p>Employee salary calculations</p>
                </div>
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
                                <th>Department</th>
                                <th>Base Salary</th>
                                <th>Working Days</th>
                                <th>Present Days</th>
                                <th>Per Day</th>
                                <th>Earned Salary</th>
                                <th>Deduction</th>
                            </tr>
                        </thead>
                        <tbody>
                            {employees
                                .filter(emp => emp.salary)
                                .map((emp) => {
                                    const payroll = calculatePayroll(emp);
                                    if (!payroll) return null;
                                    return (
                                        <tr key={emp.id}>
                                            <td>{emp.name}</td>
                                            <td>{emp.department}</td>
                                            <td>₹{payroll.baseSalary.toLocaleString()}</td>
                                            <td>{payroll.workingDays}</td>
                                            <td>{payroll.presentDays}</td>
                                            <td>₹{payroll.perDaySalary}</td>
                                            <td className="text-success">₹{parseFloat(payroll.earnedSalary).toLocaleString()}</td>
                                            <td className="text-error">₹{parseFloat(payroll.deduction).toLocaleString()}</td>
                                        </tr>
                                    );
                                })}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default PayrollPage;
