import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './DashboardPage.css';

const DashboardPage = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchStats();
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

    const adminUser = JSON.parse(localStorage.getItem('adminUser') || '{}');

    const navCards = [
        { title: 'Manage Employees', icon: '👥', path: '/employees', color: '#6366f1' },
        { title: 'Attendance Tracking', icon: '📅', path: '/attendance', color: '#8b5cf6' },
        { title: 'Holiday Management', icon: '🎉', path: '/holidays', color: '#ec4899' },
        { title: 'Leave Management', icon: '🏖️', path: '/leaves', color: '#f59e0b' },
        { title: 'Payroll', icon: '💰', path: '/payroll', color: '#10b981' },
        { title: 'Settings', icon: '⚙️', path: '/settings', color: '#3b82f6' },
    ];

    return (
        <div className="dashboard-page fade-in">
            <div className="page-header">
                <div>
                    <h1>Welcome back, {adminUser.name || 'Admin'}! 👋</h1>
                    <p>Here's what's happening with your team today</p>
                </div>
            </div>

            {loading ? (
                <div className="flex justify-center">
                    <div className="spinner"></div>
                </div>
            ) : (
                <>
                    <div className="stats-grid">
                        <div className="stat-card">
                            <div className="stat-card-header">
                                <div className="stat-card-icon" style={{ background: 'var(--info-bg)', color: 'var(--info)' }}>
                                    👥
                                </div>
                            </div>
                            <div className="stat-card-value">{stats?.totalEmployees || 0}</div>
                            <div className="stat-card-label">Total Employees</div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-card-header">
                                <div className="stat-card-icon" style={{ background: 'var(--success-bg)', color: 'var(--success)' }}>
                                    ✓
                                </div>
                            </div>
                            <div className="stat-card-value text-success">{stats?.presentToday || 0}</div>
                            <div className="stat-card-label">Present Today</div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-card-header">
                                <div className="stat-card-icon" style={{ background: 'var(--warning-bg)', color: 'var(--warning)' }}>
                                    ⏰
                                </div>
                            </div>
                            <div className="stat-card-value text-warning">{stats?.lateToday || 0}</div>
                            <div className="stat-card-label">Late Today</div>
                        </div>

                        <div className="stat-card">
                            <div className="stat-card-header">
                                <div className="stat-card-icon" style={{ background: 'var(--info-bg)', color: 'var(--info)' }}>
                                    🏖️
                                </div>
                            </div>
                            <div className="stat-card-value text-info">{stats?.onLeave || 0}</div>
                            <div className="stat-card-label">On Leave</div>
                        </div>
                    </div>

                    <div className="section-header">
                        <h2>Quick Actions</h2>
                    </div>

                    <div className="nav-cards-grid">
                        {navCards.map((card) => (
                            <div
                                key={card.path}
                                className="nav-card card"
                                onClick={() => navigate(card.path)}
                            >
                                <div className="nav-card-icon" style={{ color: card.color }}>
                                    {card.icon}
                                </div>
                                <h3>{card.title}</h3>
                            </div>
                        ))}
                    </div>
                </>
            )}
        </div>
    );
};

export default DashboardPage;
