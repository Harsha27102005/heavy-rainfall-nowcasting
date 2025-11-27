import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const Settings = () => {
    const { user, login } = useAuth(); // login used to update user context
    const [username, setUsername] = useState(user?.username || '');
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState({ type: '', text: '' });
    const [loading, setLoading] = useState(false);

    const handleUpdateProfile = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage({ type: '', text: '' });
        try {
            const response = await api.put('/auth/me', { username });
            // Update local user context by re-saving token or manually updating state
            // For simplicity, we assume the user context updates on refresh or we could expose a setUser method
            setMessage({ type: 'success', text: 'Profile updated successfully!' });
        } catch (error) {
            setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to update profile' });
        }
        setLoading(false);
    };

    const handleChangePassword = async (e) => {
        e.preventDefault();
        if (newPassword !== confirmPassword) {
            setMessage({ type: 'error', text: 'New passwords do not match' });
            return;
        }
        setLoading(true);
        setMessage({ type: '', text: '' });
        try {
            await api.post('/auth/change-password', {
                current_password: currentPassword,
                new_password: newPassword
            });
            setMessage({ type: 'success', text: 'Password changed successfully!' });
            setCurrentPassword('');
            setNewPassword('');
            setConfirmPassword('');
        } catch (error) {
            setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to change password' });
        }
        setLoading(false);
    };

    return (
        <div className="page-container">
            <h1 className="section-title">Account Settings</h1>

            <div style={styles.grid}>
                {/* Profile Section */}
                <div className="glass-panel" style={styles.card}>
                    <h2 style={styles.cardTitle}>Profile Information</h2>
                    <form onSubmit={handleUpdateProfile} style={styles.form}>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Email</label>
                            <input
                                type="email"
                                value={user?.email}
                                disabled
                                style={{ ...styles.input, opacity: 0.7, cursor: 'not-allowed' }}
                            />
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Username</label>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                style={styles.input}
                                required
                            />
                        </div>
                        <button type="submit" className="primary-btn" disabled={loading}>
                            {loading ? 'Saving...' : 'Update Profile'}
                        </button>
                    </form>
                </div>

                {/* Password Section */}
                <div className="glass-panel" style={styles.card}>
                    <h2 style={styles.cardTitle}>Change Password</h2>
                    <form onSubmit={handleChangePassword} style={styles.form}>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Current Password</label>
                            <input
                                type="password"
                                value={currentPassword}
                                onChange={(e) => setCurrentPassword(e.target.value)}
                                style={styles.input}
                                required
                            />
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>New Password</label>
                            <input
                                type="password"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                                style={styles.input}
                                required
                            />
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Confirm New Password</label>
                            <input
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                style={styles.input}
                                required
                            />
                        </div>
                        <button type="submit" className="primary-btn" disabled={loading}>
                            {loading ? 'Changing...' : 'Change Password'}
                        </button>
                    </form>
                </div>
            </div>

            {message.text && (
                <div style={{
                    ...styles.message,
                    background: message.type === 'error' ? 'rgba(255, 0, 80, 0.2)' : 'rgba(0, 255, 128, 0.2)',
                    borderColor: message.type === 'error' ? '#ff0050' : '#00ff80'
                }}>
                    {message.text}
                </div>
            )}
        </div>
    );
};

const styles = {
    grid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
        gap: '2rem',
        marginTop: '2rem',
    },
    card: {
        padding: '2rem',
    },
    cardTitle: {
        fontSize: '1.2rem',
        marginBottom: '1.5rem',
        color: 'var(--primary-color)',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: '1.2rem',
    },
    formGroup: {
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem',
    },
    label: {
        fontSize: '0.9rem',
        color: 'var(--text-muted)',
    },
    input: {
        width: '100%',
        boxSizing: 'border-box',
    },
    message: {
        marginTop: '2rem',
        padding: '1rem',
        borderRadius: '8px',
        border: '1px solid',
        textAlign: 'center',
    }
};

export default Settings;
