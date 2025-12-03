import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useToast } from '../context/ToastContext';
import './LoginPage.css';

const LoginPage = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { showSuccess, showError } = useToast();

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await axios.post('http://localhost:8000/login', {
                username,
                password
            });

            if (response.data.status === 'success') {
                localStorage.setItem('isAuthenticated', 'true');
                localStorage.setItem('adminUser', JSON.stringify(response.data.user));
                showSuccess('Login successful!');
                navigate('/dashboard');
            }
        } catch (error) {
            showError(error.response?.data?.detail || 'Login failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-container glass">
                <div className="login-header">
                    <h1>🔐 Admin Login</h1>
                    <p>Sign in to access the admin panel</p>
                </div>
                <form onSubmit={handleLogin}>
                    <div className="form-group">
                        <label>Username</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter username"
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter password"
                            required
                        />
                    </div>
                    <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                        {loading ? 'Signing in...' : 'Sign In'}
                    </button>
                </form>
                <div className="login-footer">
                    <button className="btn btn-secondary" onClick={() => navigate('/')}>
                        ← Back to Welcome
                    </button>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
