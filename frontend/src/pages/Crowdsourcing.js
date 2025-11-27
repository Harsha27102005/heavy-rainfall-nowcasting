import React, { useState } from 'react';
import api from '../services/api';

const Crowdsourcing = () => {
    const [submitted, setSubmitted] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [formData, setFormData] = useState({
        location: '',
        intensity: '',
        description: ''
    });

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            await api.post('/crowdsource/report', formData);
            setSubmitted(true);
            setFormData({ location: '', intensity: '', description: '' }); // Reset form
        } catch (err) {
            console.error("Error submitting report:", err);
            setError("Failed to submit report. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page-container">
            <h1 className="section-title">Report Rainfall</h1>

            <div className="glass-panel" style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto' }}>
                {!submitted ? (
                    <form onSubmit={handleSubmit}>
                        <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
                            Help us improve our accuracy by reporting current weather conditions in your area.
                        </p>

                        {error && <div style={{ color: 'red', marginBottom: '1rem' }}>{error}</div>}

                        <div style={styles.formGroup}>
                            <label style={styles.label}>Current Location</label>
                            <input
                                type="text"
                                name="location"
                                value={formData.location}
                                onChange={handleChange}
                                placeholder="Enter area name or pin code"
                                required
                                style={styles.input}
                            />
                        </div>

                        <div style={styles.formGroup}>
                            <label style={styles.label}>Rainfall Intensity</label>
                            <select
                                name="intensity"
                                value={formData.intensity}
                                onChange={handleChange}
                                style={styles.select}
                                required
                            >
                                <option style={styles.opt} value="">Select Intensity</option>
                                <option style={styles.opt} value="none">No Rain</option>
                                <option style={styles.opt} value="light">Light Drizzle</option>
                                <option style={styles.opt} value="moderate">Moderate Rain</option>
                                <option style={styles.opt} value="heavy">Heavy Rain</option>
                                <option style={styles.opt} value="extreme">Extreme / Flood-like</option>
                            </select>
                        </div>

                        <div style={styles.formGroup}>
                            <label style={styles.label}>Description (Optional)</label>
                            <textarea
                                name="description"
                                value={formData.description}
                                onChange={handleChange}
                                rows="4"
                                placeholder="Any additional details..."
                                style={styles.input}
                            ></textarea>
                        </div>

                        <button type="submit" className="primary-btn" style={{ width: '100%', fontFamily: 'var(--font-main)', fontSize: '1rem', letterSpacing: '0.07rem' }} disabled={loading}>
                            {loading ? 'Submitting...' : 'Submit Report'}
                        </button>
                    </form>
                ) : (
                    <div style={{ textAlign: 'center', padding: '2rem' }}>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
                        <h2 style={{ color: 'var(--primary-color)' }}>Thank You!</h2>
                        <p style={{ color: 'var(--text-muted)' }}>Your report has been submitted and will help in our analysis.</p>
                        <button
                            className="primary-btn"
                            onClick={() => setSubmitted(false)}
                            style={{ marginTop: '2rem', width: '100%', fontFamily: 'var(--font-main)', fontSize: '1rem', letterSpacing: '0.07rem' }}
                        >
                            Submit Another Report
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

const styles = {
    formGroup: { marginBottom: '1.5rem' },
    label: { display: 'block', marginBottom: '0.5rem', color: 'var(--text-color)' },
    opt: { color: 'var(--text-color)', background: '#3b3b4c' },
    input: {
        width: '100%',
        padding: '0.8rem',
        background: 'rgba(255,255,255,0.05)',
        border: '1px solid var(--glass-border)',
        borderRadius: '8px',
        color: 'var(--text-color)',
        boxSizing: 'border-box',
    },
    select: {
        width: '100%',
        padding: '0.8rem',
        paddingRight: '2.5rem',
        background: 'rgba(255,255,255,0.05)',
        border: '1px solid var(--glass-border)',
        borderRadius: '8px',
        color: 'var(--text-color)',
        boxSizing: 'border-box',
        appearance: 'none',
        backgroundImage: `url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23FFFFFF%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E")`,
        backgroundRepeat: 'no-repeat',
        backgroundPosition: 'right 1rem center',
        backgroundSize: '0.5rem',
        backgroundColor: 'rgba(255,255,255,0.05)',
    }
};

export default Crowdsourcing;
