import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

const ForgotPassword = () => {
    const [email, setEmail] = useState('');
    const [otp, setOtp] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [step, setStep] = useState(1); // 1: Request OTP, 2: Reset Password
    const [message, setMessage] = useState({ type: '', text: '' });
    const [loading, setLoading] = useState(false);

    const handleRequestOtp = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage({ type: '', text: '' });
        try {
            await api.post('/auth/forgot-password', { email });
            setStep(2);
            setMessage({ type: 'success', text: 'OTP sent to your email (check console if testing).' });
        } catch (error) {
            setMessage({ type: 'error', text: 'Failed to send OTP. Try again.' });
        }
        setLoading(false);
    };

    const handleResetPassword = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage({ type: '', text: '' });
        try {
            await api.post('/auth/reset-password', {
                email,
                otp,
                new_password: newPassword
            });
            setMessage({ type: 'success', text: 'Password reset successfully! You can now login.' });
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } catch (error) {
            setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to reset password' });
        }
        setLoading(false);
    };

    return (
        <div style={styles.container}>
            <div className="glass-panel" style={styles.card}>
                <h2 style={styles.title}>Reset Password</h2>

                {step === 1 ? (
                    <form onSubmit={handleRequestOtp} style={styles.form}>
                        <p style={styles.text}>Enter your email address to receive a password reset OTP.</p>
                        <input
                            type="email"
                            placeholder="Email Address"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                            style={styles.input}
                        />
                        <button type="submit" className="primary-btn" disabled={loading}>
                            {loading ? 'Sending...' : 'Send OTP'}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleResetPassword} style={styles.form}>
                        <p style={styles.text}>Enter the OTP sent to {email} and your new password.</p>
                        <input
                            type="text"
                            placeholder="Enter OTP"
                            value={otp}
                            onChange={(e) => setOtp(e.target.value)}
                            required
                            style={styles.input}
                        />
                        <input
                            type="password"
                            placeholder="New Password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            required
                            style={styles.input}
                        />
                        <button type="submit" className="primary-btn" disabled={loading}>
                            {loading ? 'Resetting...' : 'Reset Password'}
                        </button>
                    </form>
                )}

                {message.text && (
                    <div style={{
                        ...styles.message,
                        color: message.type === 'error' ? '#ff0050' : '#00ff80'
                    }}>
                        {message.text}
                    </div>
                )}

                <div style={styles.footer}>
                    <Link to="/login" style={styles.link}>Back to Login</Link>
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: {
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem',
    },
    card: {
        width: '100%',
        maxWidth: '400px',
        padding: '2.5rem',
        textAlign: 'center',
    },
    title: {
        fontSize: '1.8rem',
        marginBottom: '1.5rem',
        color: 'var(--primary-color)',
    },
    text: {
        color: 'var(--text-muted)',
        marginBottom: '1.5rem',
        fontSize: '0.9rem',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
    },
    input: {
        width: '100%',
        boxSizing: 'border-box',
    },
    message: {
        marginTop: '1rem',
        fontSize: '0.9rem',
    },
    footer: {
        marginTop: '2rem',
        borderTop: '1px solid var(--glass-border)',
        paddingTop: '1rem',
    },
    link: {
        fontSize: '0.9rem',
    }
};

export default ForgotPassword;
