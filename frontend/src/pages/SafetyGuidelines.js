import React from 'react';

const SafetyGuidelines = () => {
    return (
        <div className="page-container">
            <h1 className="section-title">Safety Guidelines</h1>

            <div className="glass-panel" style={{ padding: '2rem' }}>
                <h2 style={{ color: '#ff0050', marginBottom: '1.5rem' }}>⚠️ During Heavy Rainfall & Floods</h2>

                <div style={styles.grid}>
                    <div style={styles.card}>
                        <h3 style={styles.doTitle}>✅ DO's</h3>
                        <ul style={styles.list}>
                            <li>Keep emergency numbers handy (108, 1070).</li>
                            <li>Switch off electrical and gas appliances.</li>
                            <li>Keep a first aid kit, candles, and torch ready.</li>
                            <li>Move to higher ground if you live in low-lying areas.</li>
                            <li>Drink boiled or chlorinated water.</li>
                        </ul>
                    </div>

                    <div style={styles.card}>
                        <h3 style={styles.dontTitle}>❌ DON'Ts</h3>
                        <ul style={styles.list}>
                            <li>Do not walk through flowing water.</li>
                            <li>Do not drive through flooded areas.</li>
                            <li>Do not touch electrical equipment with wet hands.</li>
                            <li>Do not ignore official warnings.</li>
                            <li>Do not spread rumors.</li>
                        </ul>
                    </div>
                </div>

                <div style={{ marginTop: '3rem' }}>
                    <h3 style={{ color: 'var(--primary-color)', marginBottom: '1rem' }}>Emergency Kit Checklist</h3>
                    <div style={styles.checklist}>
                        <span>🔦 Torch & Batteries</span>
                        <span>💊 First Aid Kit</span>
                        <span>💧 Clean Water</span>
                        <span>🥫 Non-perishable Food</span>
                        <span>📻 Battery-operated Radio</span>
                        <span>📄 Important Documents</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

const styles = {
    grid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '2rem',
    },
    card: {
        background: 'rgba(255,255,255,0.05)',
        padding: '1.5rem',
        borderRadius: '12px',
    },
    doTitle: { color: '#00ff80', marginBottom: '1rem' },
    dontTitle: { color: '#ff0050', marginBottom: '1rem' },
    list: {
        color: 'var(--text-color)',
        lineHeight: '1.8',
        paddingLeft: '1.5rem',
    },
    checklist: {
        display: 'flex',
        flexWrap: 'wrap',
        gap: '1rem',
    }
};

export default SafetyGuidelines;
