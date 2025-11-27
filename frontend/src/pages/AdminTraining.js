import React, { useState, useEffect } from 'react';
import api from '../services/api';

const AdminTraining = () => {
  const [activeTab, setActiveTab] = useState('data'); // data, training, monitoring
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [logs, setLogs] = useState([]);

  // Data Management State
  const [radarFile, setRadarFile] = useState(null);
  const [labelsFile, setLabelsFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  // Monitoring State
  const [adminEmail, setAdminEmail] = useState('');
  const [adminPhone, setAdminPhone] = useState('');

  const fetchStatus = async () => {
    try {
      const response = await api.get('/training/training-status');
      setStatus(response.data);
    } catch (error) {
      console.error("Failed to fetch status", error);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleFileUpload = async (type) => {
    const file = type === 'radar' ? radarFile : labelsFile;
    if (!file) return;

    setUploading(true);
    setMessage(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const endpoint = type === 'radar' ? '/training/upload-radar-data' : '/training/upload-labels';
      await api.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setMessage({ type: 'success', text: `${type === 'radar' ? 'Radar Data' : 'Labels'} uploaded successfully!` });
      setLogs(prev => [`[${new Date().toLocaleTimeString()}] Uploaded ${file.name}`, ...prev]);

      // Reset file input and state
      if (type === 'radar') {
        setRadarFile(null);
        const input = document.getElementById('radar-file-input');
        if (input) input.value = '';
      } else {
        setLabelsFile(null);
        const input = document.getElementById('labels-file-input');
        if (input) input.value = '';
      }
    } catch (error) {
      let errorMsg = `Failed to upload ${type}`;

      // Handle different error response formats
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        // If detail is an array of validation errors
        if (Array.isArray(detail)) {
          errorMsg = detail.map(err => err.msg || JSON.stringify(err)).join(', ');
        }
        // If detail is an object
        else if (typeof detail === 'object') {
          errorMsg = detail.msg || JSON.stringify(detail);
        }
        // If detail is a string
        else {
          errorMsg = detail;
        }
      }

      setMessage({ type: 'error', text: errorMsg });
      setLogs(prev => [`[${new Date().toLocaleTimeString()}] Error uploading ${file.name}: ${errorMsg}`, ...prev]);
    }
    setUploading(false);
  };

  const handleTrain = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const response = await api.post('/training/start-training');
      setMessage({ type: 'success', text: response.data.message });
      setLogs(prev => [`[${new Date().toLocaleTimeString()}] Training started...`, ...prev]);
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to start training' });
      setLogs(prev => [`[${new Date().toLocaleTimeString()}] Error: Failed to start training`, ...prev]);
    }
    setLoading(false);
  };

  const handleStartMonitoring = async () => {
    setLoading(true);
    setMessage(null);
    try {
      await api.post('/training/start-monitoring', { admin_email: adminEmail, admin_phone: adminPhone });
      setMessage({ type: 'success', text: 'Real-time monitoring started!' });
      setLogs(prev => [`[${new Date().toLocaleTimeString()}] Monitoring started for ${adminEmail}`, ...prev]);
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to start monitoring' });
    }
    setLoading(false);
  };

  return (
    <div className="page-container">
      <h1 className="section-title">Model Training Center</h1>

      {/* Tabs */}
      <div style={styles.tabs}>
        <button
          style={{ ...styles.tab, ...(activeTab === 'data' ? styles.activeTab : {}) }}
          onClick={() => setActiveTab('data')}
        >
          1. Data Management
        </button>
        <button
          style={{ ...styles.tab, ...(activeTab === 'training' ? styles.activeTab : {}) }}
          onClick={() => setActiveTab('training')}
        >
          2. Model Training
        </button>
        <button
          style={{ ...styles.tab, ...(activeTab === 'monitoring' ? styles.activeTab : {}) }}
          onClick={() => setActiveTab('monitoring')}
        >
          3. Monitoring & Alerts
        </button>
      </div>

      <div className="glass-panel" style={styles.contentPanel}>
        {message && (
          <div style={{
            ...styles.message,
            color: message.type === 'error' ? '#ff0050' : '#00ff80',
            background: message.type === 'error' ? 'rgba(255, 0, 80, 0.1)' : 'rgba(0, 255, 128, 0.1)'
          }}>
            {message.text}
          </div>
        )}

        {/* Data Management Tab */}
        {activeTab === 'data' && (
          <div style={styles.tabContent}>
            <h2 style={styles.cardTitle}>Upload Training Data</h2>
            <p style={styles.description}>
              Upload historical radar data (.csv, .npy) and corresponding labels to train the Deep Learning models.
            </p>

            <div style={styles.uploadGrid}>
              <div style={styles.uploadCard}>
                <h3>Radar Data</h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                  Required columns: timestamp, cell_id, mcs_type, Rmj, Rmn, Theta, MeanZ, Area, Volume, Top, Base, MaxZ, MaxZhg, AvgVIL, MaxVIL, U, V, Direction, MeanRR_prev, Top10%_prev
                </p>
                <input
                  type="file"
                  accept=".csv,.xlsx,.json,.npy"
                  onChange={(e) => setRadarFile(e.target.files[0])}
                  style={styles.fileInput}
                  id="radar-file-input"
                />
                {radarFile && (
                  <p style={{ fontSize: '0.9rem', color: 'var(--secondary-color)', marginTop: '0.5rem' }}>
                    Selected: {radarFile.name}
                  </p>
                )}
                <button
                  className="primary-btn"
                  onClick={() => handleFileUpload('radar')}
                  disabled={!radarFile || uploading}
                  style={{ marginTop: '1rem', width: '100%' }}
                >
                  {uploading ? 'Uploading...' : 'Upload Radar Data'}
                </button>
              </div>

              <div style={styles.uploadCard}>
                <h3>Labels</h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                  Required columns: cell_id, mcs_type, is_heavy_rainfall, mean_rainfall_rate_mmh, top10_mean_rr_mmh
                </p>
                <input
                  type="file"
                  accept=".csv,.xlsx,.json"
                  onChange={(e) => setLabelsFile(e.target.files[0])}
                  style={styles.fileInput}
                  id="labels-file-input"
                />
                {labelsFile && (
                  <p style={{ fontSize: '0.9rem', color: 'var(--secondary-color)', marginTop: '0.5rem' }}>
                    Selected: {labelsFile.name}
                  </p>
                )}
                <button
                  className="primary-btn"
                  onClick={() => handleFileUpload('labels')}
                  disabled={!labelsFile || uploading}
                  style={{ marginTop: '1rem', width: '100%' }}
                >
                  {uploading ? 'Uploading...' : 'Upload Labels'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Model Training Tab */}
        {activeTab === 'training' && (
          <div style={styles.tabContent}>
            <h2 style={styles.cardTitle}>Train Models</h2>
            <p style={styles.description}>
              Train the 1D CNN (Classification) and Deep ANN (Regression) models using uploaded data.
            </p>

            <div style={styles.statusIndicator}>
              <span style={styles.label}>Status:</span>
              <span style={{
                ...styles.statusBadge,
                background:
                  status?.status === 'training' ? 'rgba(255, 166, 0, 0.2)' :
                    status?.status === 'completed' ? 'rgba(0, 255, 128, 0.2)' :
                      status?.status === 'failed' ? 'rgba(255, 0, 80, 0.2)' :
                        'rgba(128, 128, 128, 0.2)',
                color:
                  status?.status === 'training' ? 'orange' :
                    status?.status === 'completed' ? '#00ff80' :
                      status?.status === 'failed' ? '#ff0050' :
                        '#888',
                border:
                  status?.status === 'training' ? '1px solid orange' :
                    status?.status === 'completed' ? '1px solid #00ff80' :
                      status?.status === 'failed' ? '1px solid #ff0050' :
                        '1px solid #888'
              }}>
                {status?.status === 'training' ? '🔄 Training in Progress...' :
                  status?.status === 'completed' ? '✅ Training Completed' :
                    status?.status === 'failed' ? '❌ Training Failed' :
                      status?.status === 'not_started' ? '⏸️ Not Started' :
                        '⏸️ Idle'}
              </span>
            </div>

            {status?.status === 'failed' && status?.error_message && (
              <div style={{
                padding: '1rem',
                background: 'rgba(255, 0, 80, 0.1)',
                border: '1px solid #ff0050',
                borderRadius: '8px',
                marginBottom: '1rem',
                color: '#ff0050'
              }}>
                <strong>Error:</strong> {status.error_message}
              </div>
            )}

            {status?.status === 'completed' && (
              <div style={{
                padding: '1rem',
                background: 'rgba(0, 255, 128, 0.1)',
                border: '1px solid #00ff80',
                borderRadius: '8px',
                marginBottom: '1rem',
                color: '#00ff80'
              }}>
                ✅ Models trained successfully! You can now proceed to Monitoring & Alerts.
              </div>
            )}

            <button
              onClick={handleTrain}
              className="primary-btn"
              disabled={loading || status?.status === 'training'}
              style={{ width: '100%', maxWidth: '300px' }}
            >
              {status?.status === 'training' ? '⏳ Training Running...' :
                status?.status === 'completed' ? '🔄 Retrain Models' :
                  '▶️ Start Training'}
            </button>

            <div style={styles.logsContainer}>
              <h3>Activity Logs</h3>
              {logs.map((log, index) => (
                <div key={index} style={styles.logEntry}>{log}</div>
              ))}
            </div>
          </div>
        )}

        {/* Monitoring Tab */}
        {activeTab === 'monitoring' && (
          <div style={styles.tabContent}>
            <h2 style={styles.cardTitle}>Real-Time Monitoring</h2>
            <p style={styles.description}>
              Configure alerts and start the real-time nowcasting system.
            </p>

            <div style={styles.formGroup}>
              <label>Admin Email (for Alerts)</label>
              <input
                type="email"
                value={adminEmail}
                onChange={(e) => setAdminEmail(e.target.value)}
                placeholder="admin@example.com"
                style={styles.input}
              />
            </div>

            <div style={styles.formGroup}>
              <label>Admin Phone (for SMS)</label>
              <input
                type="tel"
                value={adminPhone}
                onChange={(e) => setAdminPhone(e.target.value)}
                placeholder="+1234567890"
                style={styles.input}
              />
            </div>

            <button
              onClick={handleStartMonitoring}
              className="primary-btn"
              disabled={loading || !adminEmail}
              style={{ width: '100%', maxWidth: '300px', marginTop: '1rem' }}
            >
              Start Monitoring System
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

const styles = {
  tabs: {
    display: 'flex',
    gap: '1rem',
    marginBottom: '2rem',
    borderBottom: '1px solid var(--glass-border)',
    paddingBottom: '1rem',
  },
  tab: {
    background: 'transparent',
    border: 'none',
    color: 'var(--text-muted)',
    padding: '0.5rem 1rem',
    cursor: 'pointer',
    fontSize: '1rem',
    fontWeight: '500',
    transition: 'all 0.3s',
    borderRadius: '8px',
  },
  activeTab: {
    background: 'rgba(255, 255, 255, 0.1)',
    color: 'var(--secondary-color)',
  },
  contentPanel: {
    padding: '2rem',
    minHeight: '500px',
  },
  cardTitle: {
    fontSize: '1.5rem',
    marginBottom: '1rem',
    color: 'var(--primary-color)',
  },
  description: {
    color: 'var(--text-muted)',
    marginBottom: '2rem',
    maxWidth: '600px',
  },
  uploadGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '2rem',
  },
  uploadCard: {
    background: 'rgba(0,0,0,0.2)',
    padding: '1.5rem',
    borderRadius: '12px',
    border: '1px solid var(--glass-border)',
  },
  fileInput: {
    width: '100%',
    padding: '0.5rem',
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid var(--glass-border)',
    borderRadius: '8px',
    color: 'var(--text-color)',
    marginTop: '1rem',
  },
  statusIndicator: {
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    marginBottom: '2rem',
  },
  statusBadge: {
    padding: '0.4rem 1rem',
    borderRadius: '20px',
    fontSize: '0.9rem',
    fontWeight: '600',
  },
  logsContainer: {
    marginTop: '2rem',
    background: 'rgba(0,0,0,0.3)',
    padding: '1rem',
    borderRadius: '8px',
    maxHeight: '300px',
    overflowY: 'auto',
    fontFamily: 'monospace',
  },
  logEntry: {
    marginBottom: '0.5rem',
    fontSize: '0.9rem',
    color: 'var(--text-muted)',
    borderBottom: '1px solid rgba(255,255,255,0.05)',
  },
  formGroup: {
    marginBottom: '1.5rem',
    maxWidth: '400px',
  },
  input: {
    width: '100%',
    padding: '0.8rem',
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid var(--glass-border)',
    borderRadius: '8px',
    color: 'var(--text-color)',
    marginTop: '0.5rem',
  },
  message: {
    padding: '1rem',
    borderRadius: '8px',
    marginBottom: '1.5rem',
    textAlign: 'center',
  }
};

export default AdminTraining;