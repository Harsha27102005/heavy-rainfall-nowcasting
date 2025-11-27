import React, { useState, useEffect } from 'react';
import api from '../services/api';
import TimeSelector from '../components/TimeSelector';
import MapLegend from '../components/MapLegend';
import AlertsDisplay from '../components/AlertsDisplay';
import LoadingSpinner from '../components/LoadingSpinner';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polygon } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix Leaflet icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const Dashboard = () => {
    const [predictions, setPredictions] = useState([]);
    const [warnings, setWarnings] = useState([]);
    const [loading, setLoading] = useState(false);
    const [selectedTime, setSelectedTime] = useState('30min');
    const [lastUpdated, setLastUpdated] = useState(null);

    const fetchPredictions = async () => {
        setLoading(true);
        try {
            const response = await api.get(`/nowcast/${selectedTime}`);
            setPredictions(response.data.predicted_storm_cells);
            setLastUpdated(new Date(response.data.timestamp).toLocaleString());
        } catch (err) {
            console.error('Failed to fetch predictions:', err);
        }
        setLoading(false);
    };

    const fetchWarnings = async () => {
        try {
            const response = await api.get('/warnings/active');
            setWarnings(response.data);
        } catch (err) {
            console.error('Failed to fetch warnings:', err);
        }
    };

    useEffect(() => {
        fetchPredictions();
        fetchWarnings();
        const interval = setInterval(() => {
            fetchPredictions();
            fetchWarnings();
        }, 300000); // Refresh every 5 mins
        return () => clearInterval(interval);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedTime]);

    // Calculate summary stats
    const highRiskCount = predictions.filter(p => p.impact_risk === 'High').length;
    const mediumRiskCount = predictions.filter(p => p.impact_risk === 'Medium').length;

    return (
        <div className="page-container">
            <div style={styles.hero}>
                <div style={styles.heroContent}>
                    <h1 style={styles.heroTitle}>Nowcasting Dashboard</h1>
                    <p style={styles.heroSubtitle}>Real-time heavy rainfall monitoring and storm tracking system</p>
                    <div style={styles.heroBadge}>
                        <span style={styles.pulse}></span>
                        Live Monitoring Active
                    </div>
                </div>
                <div style={styles.controls}>
                    <TimeSelector selected={selectedTime} onChange={setSelectedTime} />
                    <button onClick={fetchPredictions} className="primary-btn" style={{ marginLeft: '1rem' }}>
                        Refresh Data
                    </button>
                </div>
            </div>

            {/* Stats Row */}
            <div style={styles.statsGrid}>
                <div className="glass-panel" style={styles.statCard}>
                    <h3 style={styles.statTitle}>Total Cells</h3>
                    <p style={styles.statValue}>{predictions.length}</p>
                </div>
                <div className="glass-panel" style={{ ...styles.statCard, borderLeft: '4px solid #ff4d4d' }}>
                    <h3 style={styles.statTitle}>High Risk</h3>
                    <p style={styles.statValue}>{highRiskCount}</p>
                </div>
                <div className="glass-panel" style={{ ...styles.statCard, borderLeft: '4px solid #ffa600' }}>
                    <h3 style={styles.statTitle}>Medium Risk</h3>
                    <p style={styles.statValue}>{mediumRiskCount}</p>
                </div>
                <div className="glass-panel" style={styles.statCard}>
                    <h3 style={styles.statTitle}>Last Updated</h3>
                    <p style={styles.statValueSmall}>{lastUpdated || 'Never'}</p>
                </div>
            </div>

            <div style={styles.mainContent}>
                {/* Map Section */}
                <div className="glass-panel" style={styles.mapContainer}>
                    {loading && <div style={styles.loaderOverlay}><LoadingSpinner /></div>}

                    <MapContainer
                        center={[20.5937, 78.9629]} // Center of India (approx) - adjust as needed
                        zoom={5}
                        style={{ height: '100%', width: '100%', borderRadius: '16px' }}
                    >
                        <TileLayer
                            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />

                        {predictions.map((cell) => (
                            <React.Fragment key={cell.id}>
                                <Marker position={[cell.latitude, cell.longitude]}>
                                    <Popup>
                                        <div style={styles.popup}>
                                            <h4>Storm Cell {cell.id}</h4>
                                            <p><strong>Rainfall:</strong> {cell.predicted_mean_rr.toFixed(2)} mm/h</p>
                                            <p><strong>Risk:</strong>
                                                <span style={{
                                                    color: cell.impact_risk === 'High' ? 'red' :
                                                        cell.impact_risk === 'Medium' ? 'orange' : 'green',
                                                    fontWeight: 'bold',
                                                    marginLeft: '5px'
                                                }}>
                                                    {cell.impact_risk}
                                                </span>
                                            </p>
                                        </div>
                                    </Popup>
                                </Marker>
                                <Circle
                                    center={[cell.latitude, cell.longitude]}
                                    radius={5000} // 5km radius approx
                                    pathOptions={{
                                        color: cell.impact_risk === 'High' ? 'red' :
                                            cell.impact_risk === 'Medium' ? 'orange' : 'green',
                                        fillColor: cell.impact_risk === 'High' ? 'red' :
                                            cell.impact_risk === 'Medium' ? 'orange' : 'green',
                                        fillOpacity: 0.2
                                    }}
                                />
                            </React.Fragment>
                        ))}

                        {/* Display Warning Polygons */}
                        {warnings.map((warning, index) => {
                            // Extract coordinates from GeoJSON
                            const coordinates = warning.location_geojson?.coordinates?.[0] || [];
                            // Convert [lng, lat] to [lat, lng] for Leaflet
                            const positions = coordinates.map(coord => [coord[1], coord[0]]);

                            return (
                                <Polygon
                                    key={warning._id || warning.cell_id || index}
                                    positions={positions}
                                    pathOptions={{
                                        color: '#ff0000',
                                        fillColor: '#ff0000',
                                        fillOpacity: 0.3,
                                        weight: 3
                                    }}
                                >
                                    <Popup>
                                        <div style={styles.popup}>
                                            <h4 style={{ color: '#ff0000', fontWeight: 'bold' }}>⚠️ WARNING</h4>
                                            <p><strong>Cell ID:</strong> {warning.cell_id}</p>
                                            <p><strong>Type:</strong> {warning.mcs_type}</p>
                                            <p><strong>Rain Rate:</strong> {warning.predicted_top_10_rain_rate} mm/h</p>
                                            <p><strong>Forecast:</strong> {warning.forecast_time} min</p>
                                            <p style={{ fontSize: '0.85rem', marginTop: '0.5rem' }}>{warning.message}</p>
                                        </div>
                                    </Popup>
                                </Polygon>
                            );
                        })}
                    </MapContainer>

                    <div style={styles.legendOverlay}>
                        <MapLegend />
                    </div>
                </div>

                {/* Alerts Section */}
                <div className="glass-panel" style={styles.alertsContainer}>
                    <h2 style={styles.cardTitle}>Active Alerts</h2>
                    <AlertsDisplay alerts={warnings} />
                </div>
            </div>
        </div>
    );
};

const styles = {
    hero: {
        background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        borderRadius: '24px',
        padding: '3rem',
        marginTop: '3rem',
        marginBottom: '3rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '2rem',
        border: '1px solid var(--glass-border)',
        boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.15)',
    },
    heroContent: {
        flex: 1,
        minWidth: '300px',
    },
    heroTitle: {
        fontSize: '3rem',
        fontWeight: '800',
        background: 'linear-gradient(to right, var(--primary-color), var(--secondary-color))',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        marginBottom: '1rem',
        letterSpacing: '2px',
    },
    heroSubtitle: {
        fontSize: '1.2rem',
        color: 'var(--text-muted)',
        marginBottom: '1.5rem',
    },
    heroBadge: {
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.5rem',
        padding: '0.5rem 1rem',
        background: 'rgba(0, 255, 128, 0.1)',
        border: '1px solid rgba(0, 255, 128, 0.2)',
        borderRadius: '20px',
        color: '#00ff80',
        fontSize: '0.9rem',
        fontWeight: '600',
    },
    pulse: {
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        background: '#00ff80',
        boxShadow: '0 0 0 rgba(0, 255, 128, 0.4)',
        animation: 'pulse 2s infinite',
    },
    controls: {
        display: 'flex',
        alignItems: 'center',
    },
    statsGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1.5rem',
        marginBottom: '2rem',
    },
    statCard: {
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
    },
    statTitle: {
        fontSize: '0.9rem',
        color: 'var(--text-muted)',
        marginBottom: '0.5rem',
        fontWeight: '500',
    },
    statValue: {
        fontSize: '2rem',
        fontWeight: '700',
        color: 'var(--text-color)',
        margin: 0,
    },
    statValueSmall: {
        fontSize: '1.2rem',
        fontWeight: '600',
        color: 'var(--text-color)',
        margin: 0,
    },
    mainContent: {
        display: 'grid',
        gridTemplateColumns: '2fr 1fr',
        gap: '2rem',
        height: '600px',
    },
    mapContainer: {
        position: 'relative',
        height: '100%',
        overflow: 'hidden',
        padding: '0', // Map takes full space
    },
    loaderOverlay: {
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
    },
    legendOverlay: {
        position: 'absolute',
        bottom: '20px',
        right: '20px',
        zIndex: 999,
    },
    alertsContainer: {
        padding: '1.5rem',
        overflowY: 'auto',
    },
    cardTitle: {
        fontSize: '1.2rem',
        marginBottom: '1rem',
        color: 'var(--primary-color)',
        borderBottom: '1px solid var(--glass-border)',
        paddingBottom: '0.5rem',
    },
    popup: {
        color: '#333', // Leaflet popups are usually white bg
    }
};

export default Dashboard;