import React from 'react';

const About = () => {
    return (
        <div className="page-container">
            <h1 className="section-title">About Us</h1>

            <div className="glass-panel" style={{ padding: '3rem' }}>
                <h2 style={{ color: 'var(--primary-color)', marginBottom: '1rem' }}>Our Mission</h2>
                <p style={styles.text}>
                    The Heavy Rainfall Nowcasting System aims to provide accurate, real-time short-term weather predictions to mitigate the impact of urban flooding and heavy precipitation events. By leveraging advanced Deep Learning technologies, we strive to give authorities and citizens the precious lead time needed to save lives and property.
                </p>

                <div style={styles.divider}></div>

                <h2 style={{ color: 'var(--primary-color)', marginBottom: '1rem' }}>Technology Stack</h2>
                <div style={styles.grid}>
                    <div style={styles.card}>
                        <h3>🧠 1D CNN</h3>
                        <p style={styles.cardText}>
                            Our Convolutional Neural Network (CNN) processes complex radar data to classify and track storm cells with high precision.
                        </p>
                    </div>
                    <div style={styles.card}>
                        <h3>📉 Deep ANN</h3>
                        <p style={styles.cardText}>
                            A Deep Artificial Neural Network (ANN) analyzes atmospheric parameters to regress and predict exact rainfall rates (mm/h).
                        </p>
                    </div>
                    <div style={styles.card}>
                        <h3>⚡ FastAPI & React</h3>
                        <p style={styles.cardText}>
                            Built on a high-performance Python backend and a modern, responsive React frontend for seamless user experience.
                        </p>
                    </div>
                </div>

                {/*<div style={styles.divider}></div>

                <h2 style={{ color: 'var(--primary-color)', marginBottom: '1rem' }}>The Team</h2>
                <p style={styles.text}>
                    Developed by Batch-11 for Team Project on Disaster Management.
                </p>*/}
            </div>
        </div>
    );
};

const styles = {
    text: {
        color: 'var(--text-muted)',
        lineHeight: '1.8',
        fontSize: '1.1rem',
        maxWidth: '1200px',
        justifyContent: 'justify',
    },
    divider: {
        height: '1px',
        background: 'var(--glass-border)',
        margin: '3rem 0',
    },
    grid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '2rem',
        marginTop: '2rem',
    },
    card: {
        background: 'rgba(255,255,255,0.05)',
        padding: '1.5rem',
        borderRadius: '12px',
        border: '1px solid var(--glass-border)',
    },
    cardText: {
        color: 'var(--text-muted)',
        marginTop: '0.5rem',
        lineHeight: '1.6',
    }
};

export default About;
