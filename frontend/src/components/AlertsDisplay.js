// frontend/src/components/AlertsDisplay.js
import React from 'react';

const AlertsDisplay = ({ alerts }) => {
    if (!alerts || alerts.length === 0) {
        return (
            <div style={styles.emptyState}>
                <p style={styles.emptyText}>✅ No active alerts</p>
                <p style={styles.emptySubtext}>All clear - no heavy rainfall warnings at this time</p>
            </div>
        );
    }

    return (
        <div style={styles.container}>
            {alerts.map((alert, index) => {
                // Extract severity from the database field or parse from cell_id
                let severity = alert.severity;

                // If severity not in database, try to extract from cell_id
                if (!severity && alert.cell_id) {
                    const cellIdLower = alert.cell_id.toLowerCase();
                    if (cellIdLower.includes('critical')) {
                        severity = 'Critical';
                    } else if (cellIdLower.includes('severe')) {
                        severity = 'Severe';
                    } else if (cellIdLower.includes('moderate')) {
                        severity = 'Moderate';
                    } else {
                        severity = 'Moderate'; // Default
                    }
                }

                const severityColor =
                    severity === 'Critical' ? '#ff0050' :
                        severity === 'Severe' ? '#ff6b00' :
                            '#ffa600';

                return (
                    <div key={alert._id || alert.cell_id || index} style={{
                        ...styles.alertCard,
                        borderLeft: `4px solid ${severityColor}`
                    }}>
                        <div style={styles.cardHeader}>
                            <div style={styles.headerLeft}>
                                <span style={styles.icon}>⚠️</span>
                                <div>
                                    <h4 style={styles.title}>{alert.cell_id}</h4>
                                    <span style={{
                                        ...styles.severityBadge,
                                        background: `${severityColor}20`,
                                        color: severityColor,
                                        border: `1px solid ${severityColor}`
                                    }}>
                                        {severity.toUpperCase()}
                                    </span>
                                </div>
                            </div>
                            <div style={styles.rainRate}>
                                <div style={styles.rainValue}>{alert.predicted_top_10_rain_rate}</div>
                                <div style={styles.rainUnit}>mm/h</div>
                            </div>
                        </div>

                        <div style={styles.cardBody}>
                            <p style={styles.message}>{alert.message}</p>
                        </div>

                        <div style={styles.cardFooter}>
                            <div style={styles.metaItem}>
                                <span style={styles.metaLabel}>Type:</span>
                                <span style={styles.metaValue}>{alert.mcs_type}</span>
                            </div>
                            <div style={styles.metaItem}>
                                <span style={styles.metaLabel}>Forecast:</span>
                                <span style={styles.metaValue}>{alert.forecast_time} min</span>
                            </div>
                            <div style={styles.metaItem}>
                                <span style={styles.metaLabel}>Issued:</span>
                                <span style={styles.metaValue}>
                                    {new Date(alert.issued_at).toLocaleTimeString()}
                                </span>
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

const styles = {
    container: {
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        maxHeight: '600px',
        overflowY: 'auto',
        paddingRight: '0.5rem'
    },
    emptyState: {
        textAlign: 'center',
        padding: '2rem 1rem',
        background: 'rgba(0, 255, 128, 0.05)',
        borderRadius: '12px',
        border: '1px solid rgba(0, 255, 128, 0.1)'
    },
    emptyText: {
        fontSize: '1.1rem',
        color: '#00ff80',
        fontWeight: '600',
        marginBottom: '0.5rem'
    },
    emptySubtext: {
        fontSize: '0.9rem',
        color: 'var(--text-muted)',
        margin: 0
    },
    alertCard: {
        background: 'rgba(255, 255, 255, 0.03)',
        borderRadius: '12px',
        padding: '1rem',
        border: '1px solid var(--glass-border)',
        backdropFilter: 'blur(10px)',
        transition: 'all 0.3s ease',
        cursor: 'pointer'
    },
    cardHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: '0.75rem'
    },
    headerLeft: {
        display: 'flex',
        gap: '0.75rem',
        alignItems: 'flex-start',
        flex: 1
    },
    icon: {
        fontSize: '1.5rem',
        lineHeight: 1
    },
    title: {
        fontSize: '1rem',
        fontWeight: '700',
        color: 'var(--text-primary)',
        margin: '0 0 0.25rem 0',
        letterSpacing: '0.5px'
    },
    severityBadge: {
        fontSize: '0.7rem',
        fontWeight: '700',
        padding: '0.2rem 0.5rem',
        borderRadius: '4px',
        display: 'inline-block',
        letterSpacing: '0.5px'
    },
    rainRate: {
        textAlign: 'right'
    },
    rainValue: {
        fontSize: '1.5rem',
        fontWeight: '800',
        color: '#ff0050',
        lineHeight: 1
    },
    rainUnit: {
        fontSize: '0.7rem',
        color: 'var(--text-muted)',
        fontWeight: '600'
    },
    cardBody: {
        marginBottom: '0.75rem'
    },
    message: {
        fontSize: '0.85rem',
        color: 'var(--text-secondary)',
        lineHeight: '1.5',
        margin: 0
    },
    cardFooter: {
        display: 'flex',
        gap: '1rem',
        paddingTop: '0.75rem',
        borderTop: '1px solid var(--glass-border)',
        flexWrap: 'wrap'
    },
    metaItem: {
        display: 'flex',
        flexDirection: 'column',
        gap: '0.2rem'
    },
    metaLabel: {
        fontSize: '0.7rem',
        color: 'var(--text-muted)',
        fontWeight: '600',
        textTransform: 'uppercase',
        letterSpacing: '0.5px'
    },
    metaValue: {
        fontSize: '0.85rem',
        color: 'var(--text-primary)',
        fontWeight: '600'
    }
};

export default AlertsDisplay;