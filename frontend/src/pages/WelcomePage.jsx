import React, { useRef, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { MdSettings } from 'react-icons/md';
import PunchOutModal from '../components/PunchOutModal';
import './WelcomePage.css';

const WelcomePage = () => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const particleCanvasRef = useRef(null);
    const [stream, setStream] = useState(null);
    const [recognizedEmployee, setRecognizedEmployee] = useState(null);
    const [message, setMessage] = useState(null);
    const [showPunchOut, setShowPunchOut] = useState(false);
    const [scanning, setScanning] = useState(false);
    const [currentTime, setCurrentTime] = useState(new Date());
    const [showConfetti, setShowConfetti] = useState(false);
    const [showSparkles, setShowSparkles] = useState(false);
    const navigate = useNavigate();

    // Particle animation
    useEffect(() => {
        const canvas = particleCanvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const particles = [];
        const particleCount = 50;

        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.size = Math.random() * 3 + 1;
                this.speedX = Math.random() * 0.5 - 0.25;
                this.speedY = Math.random() * 0.5 - 0.25;
                this.opacity = Math.random() * 0.5 + 0.3;
            }

            update() {
                this.x += this.speedX;
                this.y += this.speedY;

                if (this.x > canvas.width) this.x = 0;
                if (this.x < 0) this.x = canvas.width;
                if (this.y > canvas.height) this.y = 0;
                if (this.y < 0) this.y = canvas.height;
            }

            draw() {
                ctx.fillStyle = `rgba(99, 102, 241, ${this.opacity})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        for (let i = 0; i < particleCount; i++) {
            particles.push(new Particle());
        }

        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(particle => {
                particle.update();
                particle.draw();
            });
            requestAnimationFrame(animate);
        }

        animate();

        const handleResize = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    useEffect(() => {
        startCamera();
        const timeInterval = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => {
            stopCamera();
            clearInterval(timeInterval);
        };
    }, []);

    useEffect(() => {
        if (stream && !scanning && !message) {
            const scanInterval = setInterval(() => {
                scanFace();
            }, 2500);

            return () => clearInterval(scanInterval);
        }
    }, [stream, scanning, message]);

    // Auto-clear message only if NOT showing punch out option
    useEffect(() => {
        if (message && message.type === 'welcome' && !recognizedEmployee?.already_present) {
            const timer = setTimeout(() => {
                setMessage(null);
                setRecognizedEmployee(null);
            }, 5000);
            return () => clearTimeout(timer);
        }

        // Goodbye messages auto-clear
        if (message && message.type === 'goodbye') {
            const timer = setTimeout(() => {
                setMessage(null);
                setRecognizedEmployee(null);
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [message, recognizedEmployee]);

    // Confetti effect
    useEffect(() => {
        if (showConfetti) {
            const timer = setTimeout(() => setShowConfetti(false), 3000);
            return () => clearTimeout(timer);
        }
    }, [showConfetti]);

    // Sparkles effect
    useEffect(() => {
        if (showSparkles) {
            const timer = setTimeout(() => setShowSparkles(false), 2000);
            return () => clearTimeout(timer);
        }
    }, [showSparkles]);

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

    const scanFace = async () => {
        if (!videoRef.current || !canvasRef.current || message) return;

        const canvas = canvasRef.current;
        const video = videoRef.current;

        // Check if video is ready and has valid dimensions
        if (video.readyState !== video.HAVE_ENOUGH_DATA || video.videoWidth === 0 || video.videoHeight === 0) {
            return; // Don't start scanning if video isn't ready
        }

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);

        canvas.toBlob(async (blob) => {
            if (!blob) {
                return;
            }

            const formData = new FormData();
            formData.append('file', blob, 'frame.jpg');

            try {
                const response = await axios.post(
                    'http://localhost:8000/mark_attendance',
                    formData,
                    { headers: { 'Content-Type': 'multipart/form-data' } }
                );

                // Only show scanning animation when face is detected
                if (response.data.status === 'success' && response.data.name) {
                    setScanning(true); // Show scanning effect

                    // Brief delay to show the scanning animation
                    setTimeout(() => {
                        setScanning(false);
                        setRecognizedEmployee(response.data);

                        // Check if already present (coming back)
                        if (response.data.already_present) {
                            setMessage({
                                title: `Welcome back, ${response.data.name}! 👋`,
                                text: "Ready to punch out?",
                                type: 'welcome'
                            });
                        } else {
                            // First time check-in
                            setMessage({
                                title: `Welcome, ${response.data.name}! 👋`,
                                text: response.data.message,
                                type: 'welcome'
                            });
                            setShowConfetti(true); // Only show confetti on first check-in
                        }
                    }, 800); // Show scan animation for 800ms
                }
            } catch (error) {
                console.error('Scan error:', error);
            }
        }, 'image/jpeg');
    };

    const handlePunchOutSuccess = () => {
        setMessage({
            title: `Thank You, ${recognizedEmployee.name}! 🙏`,
            text: "Have a great evening! See you tomorrow.",
            type: 'goodbye'
        });
        setRecognizedEmployee(null);
        setShowSparkles(true); // Trigger sparkles
    };

    const formatDate = (date) => {
        return date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    const formatTime = (date) => {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };

    return (
        <div className="welcome-page">
            <canvas ref={particleCanvasRef} className="particle-canvas" />

            <header className="company-header">
                <h1>Nexoris</h1>
            </header>

            <div className="date-time-display">
                <div className="time">{formatTime(currentTime)}</div>
                <div className="date">{formatDate(currentTime)}</div>
            </div>

            <button className="settings-btn" onClick={() => navigate('/login')} title="Admin Panel">
                <MdSettings size={24} />
            </button>

            <div className="content-wrapper">
                <div className={`camera-card ${scanning ? 'scanning-pulse' : ''}`}>
                    <div className="camera-container">
                        <video ref={videoRef} autoPlay playsInline />
                        <canvas ref={canvasRef} style={{ display: 'none' }} />

                        {scanning && !message && (
                            <div className="scanning-indicator">
                                <div className="scan-line"></div>
                            </div>
                        )}
                    </div>
                </div>

                <div className="message-area">
                    {message && (
                        <div className={`message-card ${message.type}`}>
                            <h1>{message.title}</h1>
                            <p>{message.text}</p>

                            {recognizedEmployee && recognizedEmployee.already_present && message.type === 'welcome' && (
                                <button
                                    className="btn btn-primary mt-2"
                                    onClick={() => setShowPunchOut(true)}
                                >
                                    Punch Out
                                </button>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {showConfetti && (
                <div className="confetti-container">
                    {[...Array(50)].map((_, i) => (
                        <div
                            key={i}
                            className="confetti"
                            style={{
                                left: `${Math.random() * 100}%`,
                                animationDelay: `${Math.random() * 0.5}s`,
                                backgroundColor: ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b'][Math.floor(Math.random() * 4)]
                            }}
                        />
                    ))}
                </div>
            )}

            {showSparkles && (
                <div className="sparkles-container">
                    {[...Array(20)].map((_, i) => (
                        <div
                            key={i}
                            className="sparkle"
                            style={{
                                left: `${Math.random() * 100}%`,
                                top: `${Math.random() * 100}%`,
                                animationDelay: `${Math.random() * 0.3}s`
                            }}
                        >
                            ✨
                        </div>
                    ))}
                </div>
            )}

            {showPunchOut && recognizedEmployee && (
                <PunchOutModal
                    employeeName={recognizedEmployee.name}
                    onClose={() => setShowPunchOut(false)}
                    onSuccess={handlePunchOutSuccess}
                />
            )}
        </div>
    );
};

export default WelcomePage;
