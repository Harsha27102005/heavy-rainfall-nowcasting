import React, { useState, useEffect } from 'react';
import api from '../services/api';

const AlertBanner = () => {
    const [warnings, setWarnings] = useState([]);

    useEffect(() => {
        const fetchWarnings = async () => {
            try {
                const response = await api.get('/warnings/active');
                setWarnings(response.data);
            } catch (error) {
                console.error("Failed to fetch warnings", error);
            }
        };

        fetchWarnings();
        const interval = setInterval(fetchWarnings, 60000); // Refresh every minute
        return () => clearInterval(interval);
    }, []);

    if (warnings.length === 0) return null;

    return (
        <div style={styles.banner}>
            <div style={styles.ticker}>
                {warnings.map((warning, index) => (
                    <span key={index} style={styles.warningItem}>
                        ⚠️ WARNING: Cell {warning.cell_id} - {warning.message} (Rain Rate: {warning.predicted_top10_mean_rr}mm/h)
                    </span>
                ))}
            </div>
        </div>
    );
};

const styles = {
    banner: {
        background: '#ff0050',
        color: 'white',
        padding: '0.5rem',
        overflow: 'hidden',
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        zIndex: 2000,
        boxShadow: '0 2px 10px rgba(255, 0, 80, 0.3)',
    },
    ticker: {
        whiteSpace: 'nowrap',
        animation: 'ticker 20s linear infinite',
        display: 'inline-block',
        paddingLeft: '100%',
    },
    warningItem: {
        marginRight: '50px',
        fontWeight: 'bold',
    }
};

// Add keyframes for ticker animation
const styleSheet = document.createElement("style");
styleSheet.innerText = `
@keyframes ticker {
  0% { transform: translateX(0); }
  100% { transform: translateX(-100%); }
}
`;
document.head.appendChild(styleSheet);

export default AlertBanner;
