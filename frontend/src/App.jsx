import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link } from 'react-router-dom';
import './App.css';
import Toast from './components/Toast';

// Pages
import WelcomePage from './pages/WelcomePage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import AddRemoveEmployeePage from './pages/AddRemoveEmployeePage';
import AttendanceDashboardPage from './pages/AttendanceDashboardPage';
import HolidayManagement from './pages/HolidayManagement';
import LeaveManagement from './pages/LeaveManagement';
import PayrollPage from './pages/PayrollPage';
import SettingsPage from './pages/SettingsPage';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
    return isAuthenticated ? children : <Navigate to="/login" />;
};

// Admin Layout with Sidebar
const AdminLayout = ({ children }) => {
    const handleLogout = () => {
        localStorage.removeItem('isAuthenticated');
        localStorage.removeItem('adminUser');
        window.location.href = '/login';
    };

    return (
        <div className="admin-layout">
            <aside className="sidebar">
                <div className="sidebar-brand">
                    <h2>📊 Admin Panel</h2>
                </div>
                <nav>
                    <ul className="sidebar-nav">
                        <li>
                            <Link to="/dashboard">
                                <span>🏠</span> Dashboard
                            </Link>
                        </li>
                        <li>
                            <Link to="/employees">
                                <span>👥</span> Employees
                            </Link>
                        </li>
                        <li>
                            <Link to="/attendance">
                                <span>📅</span> Attendance
                            </Link>
                        </li>
                        <li>
                            <Link to="/holidays">
                                <span>🎉</span> Holidays
                            </Link>
                        </li>
                        <li>
                            <Link to="/leaves">
                                <span>🏖️</span> Leaves
                            </Link>
                        </li>
                        <li>
                            <Link to="/payroll">
                                <span>💰</span> Payroll
                            </Link>
                        </li>
                        <li>
                            <Link to="/settings">
                                <span>⚙️</span> Settings
                            </Link>
                        </li>
                        <li>
                            <a href="#" onClick={handleLogout} style={{ color: 'var(--error)' }}>
                                <span>🚪</span> Logout
                            </a>
                        </li>
                    </ul>
                </nav>
            </aside>
            <main className="main-content">
                {children}
            </main>
        </div>
    );
};

function App() {
    return (
        <Router>
            <div className="app">
                <Toast />
                <Routes>
                    {/* Public Routes */}
                    <Route path="/" element={<WelcomePage />} />
                    <Route path="/login" element={<LoginPage />} />

                    {/* Protected Admin Routes */}
                    <Route
                        path="/dashboard"
                        element={
                            <ProtectedRoute>
                                <AdminLayout>
                                    <DashboardPage />
                                </AdminLayout>
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/employees"
                        element={
                            <ProtectedRoute>
                                <AdminLayout>
                                    <AddRemoveEmployeePage />
                                </AdminLayout>
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/attendance"
                        element={
                            <ProtectedRoute>
                                <AdminLayout>
                                    <AttendanceDashboardPage />
                                </AdminLayout>
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/holidays"
                        element={
                            <ProtectedRoute>
                                <AdminLayout>
                                    <HolidayManagement />
                                </AdminLayout>
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/leaves"
                        element={
                            <ProtectedRoute>
                                <AdminLayout>
                                    <LeaveManagement />
                                </AdminLayout>
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/payroll"
                        element={
                            <ProtectedRoute>
                                <AdminLayout>
                                    <PayrollPage />
                                </AdminLayout>
                            </ProtectedRoute>
                        }
                    />
                    <Route
                        path="/settings"
                        element={
                            <ProtectedRoute>
                                <AdminLayout>
                                    <SettingsPage />
                                </AdminLayout>
                            </ProtectedRoute>
                        }
                    />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
