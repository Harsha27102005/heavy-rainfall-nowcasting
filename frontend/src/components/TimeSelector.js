// frontend/src/components/TimeSelector.js
import React from 'react';

const TimeSelector = ({ selected, onChange }) => {
    return (
        <div style={styles.container}>
            <button
                style={{
                    ...styles.button,
                    ...(selected === '30min' ? styles.activeButton : styles.inactiveButton)
                }}
                onClick={() => onChange('30min')}
            >
                30 Min Forecast
            </button>
            <button
                style={{
                    ...styles.button,
                    ...(selected === '60min' ? styles.activeButton : styles.inactiveButton)
                }}
                onClick={() => onChange('60min')}
            >
                60 Min Forecast
            </button>
        </div>
    );
};

const styles = {
    container: {
        display: 'flex',
        gap: '0.5rem',
        padding: '0.5rem',
        background: 'rgba(255, 255, 255, 0.05)',
        borderRadius: '12px',
        border: '1px solid var(--glass-border)',
    },
    button: {
        padding: '0.6rem 1.2rem',
        borderRadius: '8px',
        fontSize: '0.9rem',
        fontWeight: '600',
        cursor: 'pointer',
        border: 'none',
        transition: 'all 0.3s ease',
        flex: 1,
    },
    activeButton: {
        background: 'linear-gradient(90deg, var(--primary-color), var(--secondary-color))',
        color: '#fff',
        boxShadow: '0 4px 12px rgba(79, 172, 254, 0.3)',
    },
    inactiveButton: {
        background: 'transparent',
        color: 'var(--text-muted)',
    }
};

export default TimeSelector;