import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
    return (
        <footer style={styles.footer}>
            <div style={styles.container}>
                <div style={styles.column}>
                    <h3 style={styles.title}>Rainfall<span style={{ color: 'var(--secondary-color)' }}>Now</span></h3>
                    <p style={styles.text}>
                        Advanced heavy rainfall nowcasting system using Deep Learning (1D CNN & Deep ANN) for accurate storm tracking and early warnings.
                    </p>
                </div>

                <div style={styles.column}>
                    <h4 style={styles.subtitle}>Quick Links</h4>
                    <Link to="/" style={styles.link}>Dashboard</Link>
                    <Link to="/guidelines" style={styles.link}>Safety Guidelines</Link>
                    <Link to="/report" style={styles.link}>Report Rainfall</Link>
                    <Link to="/about" style={styles.link}>About Us</Link>
                </div>

                <div style={styles.column}>
                    <h4 style={styles.subtitle}>Emergency Contact</h4>
                    <p style={styles.text}>📞 Disaster Management: 108</p>
                    <p style={styles.text}>📞 Flood Control: 1070</p>
                    <p style={styles.text}>📧 help@nowcasting.com</p>
                </div>
            </div>
            <div style={styles.copyright}>
                &copy; {new Date().getFullYear()} Heavy Rainfall Nowcasting System. All rights reserved.
            </div>
        </footer>
    );
};

const styles = {
    footer: {
        background: 'rgba(0, 0, 0, 0.8)',
        backdropFilter: 'blur(10px)',
        padding: '3rem 0 1rem 0',
        marginTop: 'auto',
        borderTop: '1px solid var(--glass-border)',
    },
    container: {
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0 2rem',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '2rem',
    },
    column: {
        display: 'flex',
        flexDirection: 'column',
    },
    title: {
        fontSize: '1.5rem',
        color: 'var(--primary-color)',
        marginBottom: '1rem',
    },
    subtitle: {
        color: 'white',
        marginBottom: '1rem',
        fontSize: '1.1rem',
    },
    text: {
        color: 'var(--text-muted)',
        lineHeight: '1.6',
        marginBottom: '0.5rem',
    },
    link: {
        color: 'var(--text-muted)',
        textDecoration: 'none',
        marginBottom: '0.5rem',
        transition: 'color 0.3s',
    },
    copyright: {
        textAlign: 'center',
        color: 'var(--text-muted)',
        marginTop: '3rem',
        paddingTop: '1rem',
        borderTop: '1px solid rgba(255,255,255,0.1)',
        fontSize: '0.9rem',
    }
};

export default Footer;
