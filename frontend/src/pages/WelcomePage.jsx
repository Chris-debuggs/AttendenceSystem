import React, { useRef, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import PunchOutModal from '../components/PunchOutModal';
import './WelcomePage.css';

const WelcomePage = () => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [stream, setStream] = useState(null);
    const [recognizedEmployee, setRecognizedEmployee] = useState(null);
    const [stats, setStats] = useState(null);
    const [showWelcome, setShowWelcome] = useState(false);
    const [showPunchOut, setShowPunchOut] = useState(false);
    const [scanning, setScanning] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        startCamera();
        fetchStats();
        const statsInterval = setInterval(fetchStats, 10000); // Update stats every 10 seconds

        return () => {
            stopCamera();
            clearInterval(statsInterval);
        };
    }, []);

    useEffect(() => {
        if (stream && !scanning) {
            const scanInterval = setInterval(() => {
                scanFace();
            }, 2500); // Scan every 2.5 seconds

            return () => clearInterval(scanInterval);
        }
    }, [stream, scanning]);

    const startCamera = async () => {
        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({
                video: { width: 1280, height: 720, facingMode: 'user' }
            });
            setStream(mediaStream);
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
            }
        } catch (error) {
            console.error('Failed to access camera:', error);
        }
    };

    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    };

    const fetchStats = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/landing-stats');
            setStats(response.data);
        } catch (error) {
            console.error('Failed to fetch stats:', error);
        }
    };

    const scanFace = async () => {
        if (!videoRef.current || !canvasRef.current || scanning) return;

        setScanning(true);
        const canvas = canvasRef.current;
        const video = videoRef.current;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);

        canvas.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append('file', blob, 'frame.jpg');

            try {
                const response = await axios.post(
                    'http://localhost:8000/mark_attendance',
                    formData,
                    { headers: { 'Content-Type': 'multipart/form-data' } }
                );

                if (response.data.status === 'success' && response.data.name) {
                    setRecognizedEmployee(response.data);
                    setShowWelcome(true);
                    fetchStats(); // Refresh stats after attendance marked

                    // Hide welcome message after 5 seconds
                    setTimeout(() => {
                        setShowWelcome(false);
                        setRecognizedEmployee(null);
                    }, 5000);
                }
            } catch (error) {
                // Silently fail for continuous scanning
                console.error('Scan error:', error);
            } finally {
                setScanning(false);
            }
        }, 'image/jpeg');
    };

    return (
        <div className="welcome-page">
            <div className="camera-container">
                <video ref={videoRef} autoPlay playsInline />
                <canvas ref={canvasRef} style={{ display: 'none' }} />

                {scanning && (
                    <div className="scanning-indicator">
                        <div className="scan-line"></div>
                        <p>Scanning...</p>
                    </div>
                )}

                {showWelcome && recognizedEmployee && (
                    <div className="welcome-overlay fade-in">
                        <div className="welcome-card glass">
                            <h1>Welcome, {recognizedEmployee.name}! 👋</h1>
                            <p className="welcome-message">{recognizedEmployee.message}</p>
                            {recognizedEmployee.already_present && (
                                <button
                                    className="btn btn-primary mt-2"
                                    onClick={() => setShowPunchOut(true)}
                                >
                                    Punch Out
                                </button>
                            )}
                        </div>
                    </div>
                )}
            </div>

            <div className="stats-sidebar glass">
                <h3>Today's Overview</h3>
                {stats ? (
                    <>
                        <div className="stat-item">
                            <div className="stat-value">{stats.totalEmployees}</div>
                            <div className="stat-label">Total Employees</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-value text-success">{stats.presentToday}</div>
                            <div className="stat-label">Present Today</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-value text-warning">{stats.lateToday}</div>
                            <div className="stat-label">Late Today</div>
                        </div>
                        <div className="stat-item">
                            <div className="stat-value text-info">{stats.onLeave}</div>
                            <div className="stat-label">On Leave</div>
                        </div>

                        {stats.recentEntries?.length > 0 && (
                            <div className="recent-entries">
                                <h4>Recent Check-ins</h4>
                                <ul>
                                    {stats.recentEntries.map((entry, idx) => (
                                        <li key={idx}>
                                            <span className="entry-name">{entry.name}</span>
                                            <span className={`entry-status badge badge-${entry.status === 'On Time' ? 'success' : 'warning'}`}>
                                                {entry.status}
                                            </span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        )}
                    </>
                ) : (
                    <div className="spinner"></div>
                )}
            </div>

            <button className="admin-btn btn btn-primary" onClick={() => navigate('/login')}>
                🔐 Admin Panel
            </button>

            {showPunchOut && recognizedEmployee && (
                <PunchOutModal
                    employeeName={recognizedEmployee.name}
                    onClose={() => setShowPunchOut(false)}
                    onSuccess={fetchStats}
                />
            )}
        </div>
    );
};

export default WelcomePage;
