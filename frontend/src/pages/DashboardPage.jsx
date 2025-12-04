import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
    FaUsers,
    FaUserCheck,
    FaClock,
    FaUmbrellaBeach,
    FaChartLine
} from 'react-icons/fa';
import './DashboardPage.css';

const DashboardPage = () => {
    const [stats, setStats] = useState(null);
    const [monthlyData, setMonthlyData] = useState([]);
    const [departmentData, setDepartmentData] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchStats();
        fetchMonthlyAttendance();
        fetchDepartmentStats();
    }, []);

    const fetchStats = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/landing-stats');
            setStats(response.data);
        } catch (error) {
            console.error('Failed to fetch stats:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchMonthlyAttendance = async () => {
        try {
            const now = new Date();
            const currentYear = now.getFullYear();
            const currentMonth = now.getMonth() + 1;

            const response = await axios.get(`http://localhost:8000/attendance/${currentYear}/${currentMonth}`);

            const last7Days = [];
            for (let i = 6; i >= 0; i--) {
                const date = new Date();
                date.setDate(date.getDate() - i);
                const day = date.getDate();

                let present = 0;
                let late = 0;
                let absent = 0;

                Object.values(response.data.attendance || {}).forEach(empData => {
                    const dayData = empData[day];
                    if (dayData) {
                        if (dayData.status === 'On Time') present++;
                        else if (dayData.status === 'Late') late++;
                    } else {
                        absent++;
                    }
                });

                last7Days.push({
                    date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                    Present: present,
                    Late: late,
                    Absent: absent
                });
            }

            setMonthlyData(last7Days);
        } catch (error) {
            console.error('Failed to fetch monthly attendance:', error);
        }
    };

    const fetchDepartmentStats = async () => {
        try {
            const response = await axios.get('http://localhost:8000/employees/');
            const employees = response.data;

            const deptCounts = {};
            employees.forEach(emp => {
                const dept = emp.department || 'Unassigned';
                deptCounts[dept] = (deptCounts[dept] || 0) + 1;
            });

            const deptArray = Object.entries(deptCounts).map(([name, value]) => ({
                name,
                value
            }));

            setDepartmentData(deptArray);
        } catch (error) {
            console.error('Failed to fetch department stats:', error);
        }
    };

    const adminUser = JSON.parse(localStorage.getItem('adminUser') || '{}');

    const statusData = [
        { name: 'Present', value: stats?.presentToday || 0, color: '#10b981' },
        { name: 'Late', value: stats?.lateToday || 0, color: '#f59e0b' },
        { name: 'On Leave', value: stats?.onLeave || 0, color: '#3b82f6' },
        { name: 'Absent', value: (stats?.totalEmployees || 0) - (stats?.presentToday || 0) - (stats?.lateToday || 0) - (stats?.onLeave || 0), color: '#ef4444' }
    ];

    return (
        <div className="dashboard-page fade-in">
            <div className="page-header">
                <div>
                    <h1>Welcome back, {adminUser.name || 'Admin'}!</h1>
                    <p>Here's what's happening with your team today</p>
                </div>
            </div>

            {loading ? (
                <div className="flex justify-center">
                    <div className="spinner"></div>
                </div>
            ) : (
                <>
                    {/* Stats Cards */}
                    <div className="stats-grid">
                        <div className="stat-card">
                            <div className="stat-card-header">
                                <div className="stat-card-icon" style={{ background: 'var(--info-bg)', color: 'var(--info)' }}>
                                    <FaUsers size={24} />
                                </div>
                            </div>
                            <div className="stat-card-value">{stats?.totalEmployees || 0}</div>
                            <div className="stat-card-label">Total Employees</div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-card-header">
                                <div className="stat-card-icon" style={{ background: 'var(--success-bg)', color: 'var(--success)' }}>
                                    <FaUserCheck size={24} />
                                </div>
                            </div>
                            <div className="stat-card-value text-success">{stats?.presentToday || 0}</div>
                            <div className="stat-card-label">Present Today</div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-card-header">
                                <div className="stat-card-icon" style={{ background: 'var(--warning-bg)', color: 'var(--warning)' }}>
                                    <FaClock size={24} />
                                </div>
                            </div>
                            <div className="stat-card-value text-warning">{stats?.lateToday || 0}</div>
                            <div className="stat-card-label">Late Today</div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-card-header">
                                <div className="stat-card-icon" style={{ background: 'var(--info-bg)', color: 'var(--info)' }}>
                                    <FaUmbrellaBeach size={24} />
                                </div>
                            </div>
                            <div className="stat-card-value text-info">{stats?.onLeave || 0}</div>
                            <div className="stat-card-label">On Leave</div>
                        </div>
                    </div>

                    {/* Charts Section */}
                    <div className="section-header">
                        <h2><FaChartLine style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} /> Attendance Analytics</h2>
                    </div>

                    <div className="charts-grid">
                        {/* Weekly Trend Chart */}
                        <div className="chart-card card">
                            <h3 className="chart-title">Weekly Attendance Trend</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={monthlyData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                    <XAxis dataKey="date" stroke="#64748b" />
                                    <YAxis stroke="#64748b" />
                                    <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e2e8f0' }} />
                                    <Legend />
                                    <Line type="monotone" dataKey="Present" stroke="#10b981" strokeWidth={2} />
                                    <Line type="monotone" dataKey="Late" stroke="#f59e0b" strokeWidth={2} />
                                    <Line type="monotone" dataKey="Absent" stroke="#ef4444" strokeWidth={2} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>

                        {/* Today's Status Distribution */}
                        <div className="chart-card card">
                            <h3 className="chart-title">Today's Status Distribution</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <PieChart>
                                    <Pie
                                        data={statusData}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        dataKey="value"
                                    >
                                        {statusData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>

                        {/* Department Distribution */}
                        <div className="chart-card card">
                            <h3 className="chart-title">Department Distribution</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={departmentData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                    <XAxis dataKey="name" stroke="#64748b" />
                                    <YAxis stroke="#64748b" />
                                    <Tooltip contentStyle={{ background: '#fff', border: '1px solid #e2e8f0' }} />
                                    <Bar dataKey="value" fill="#6366f1" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>

                        {/* Recent Entries */}
                        <div className="chart-card card">
                            <h3 className="chart-title">Recent Check-ins</h3>
                            <div className="recent-entries-list">
                                {stats?.recentEntries && stats.recentEntries.length > 0 ? (
                                    stats.recentEntries.map((entry, index) => (
                                        <div key={index} className="recent-entry">
                                            <div className="recent-entry-info">
                                                <span className="recent-entry-name">{entry.name}</span>
                                                <span className="recent-entry-time">{entry.time}</span>
                                            </div>
                                            <span className={`badge badge-${entry.status === 'On Time' ? 'success' : 'warning'}`}>
                                                {entry.status}
                                            </span>
                                        </div>
                                    ))
                                ) : (
                                    <p className="text-muted">No recent entries</p>
                                )}
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default DashboardPage;
