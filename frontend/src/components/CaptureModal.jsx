import React, { useRef, useEffect, useState } from 'react';
import axios from 'axios';
import { useToast } from '../context/ToastContext';
import './CaptureModal.css';

const CaptureModal = ({ employeeId, onClose, onSuccess }) => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const [stream, setStream] = useState(null);
    const [capturing, setCapturing] = useState(false);
    const { showSuccess, showError } = useToast();

    useEffect(() => {
        startCamera();
        return () => {
            stopCamera();
        };
    }, []);

    const startCamera = async () => {
        try {
            const mediaStream = await navigator.mediaDevices.getUserMedia({
                video: { width: 640, height: 480 }
            });
            setStream(mediaStream);
            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
            }
        } catch (error) {
            showError('Failed to access camera');
        }
    };

    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    };

    const capturePhoto = async () => {
        if (!videoRef.current || !canvasRef.current) return;

        setCapturing(true);
        const canvas = canvasRef.current;
        const video = videoRef.current;

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);

        canvas.toBlob(async (blob) => {
            const formData = new FormData();
            formData.append('file', blob, 'photo.jpg');

            try {
                const response = await axios.put(
                    `http://localhost:8000/employees/${employeeId}/photo`,
                    formData,
                    { headers: { 'Content-Type': 'multipart/form-data' } }
                );

                if (response.data.status === 'success') {
                    showSuccess('Photo uploaded successfully');
                    onSuccess();
                    stopCamera();
                    onClose();
                }
            } catch (error) {
                showError(error.response?.data?.detail || 'Failed to upload photo');
            } finally {
                setCapturing(false);
            }
        }, 'image/jpeg');
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content capture-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h3>Capture Employee Photo</h3>
                </div>
                <div className="camera-preview">
                    <video ref={videoRef} autoPlay playsInline />
                    <canvas ref={canvasRef} style={{ display: 'none' }} />
                </div>
                <div className="modal-footer">
                    <button className="btn btn-secondary" onClick={onClose} disabled={capturing}>
                        Cancel
                    </button>
                    <button className="btn btn-primary" onClick={capturePhoto} disabled={capturing}>
                        {capturing ? 'Uploading...' : 'Capture Photo'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CaptureModal;
