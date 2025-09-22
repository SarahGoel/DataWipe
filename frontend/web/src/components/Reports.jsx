import React, { useState, useEffect } from 'react';
import { FaFilePdf, FaDownload, FaHistory, FaSyncAlt, FaExclamationTriangle } from 'react-icons/fa';

const API_BASE_URL = '/api';
const BACKEND_BASE_URL = '';

function Reports({ onBack, onViewCertificate }) {
  const [sessions, setSessions] = useState([]);
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('sessions');

  useEffect(() => {
    loadSessions();
    loadCertificates();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await fetch(`${API_BASE_URL}/wipe/sessions`);
      const data = await response.json();
      setSessions(data);
    } catch (err) {
      setError('Failed to load wipe sessions');
      console.error('Error loading sessions:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadCertificates = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/certificates`);
      const data = await response.json();
      setCertificates(data.certificates || []);
    } catch (err) {
      console.error('Error loading certificates:', err);
    }
  };

  const downloadReport = (sessionId) => {
    window.open(`${API_BASE_URL}/reports/${sessionId}`, '_blank');
  };

  const downloadSignature = (sessionId) => {
    window.open(`${API_BASE_URL}/reports/${sessionId}/signature`, '_blank');
  };

  const downloadJsonReport = (sessionId) => {
    window.open(`${API_BASE_URL}/reports/${sessionId}/json`, '_blank');
  };

  const viewCertificate = (certificate) => {
    if (onViewCertificate) {
      onViewCertificate(certificate);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <FaDownload className="success-icon" />;
      case 'failed':
        return <FaExclamationTriangle className="error-icon" />;
      case 'in_progress':
        return <FaSyncAlt className="spinning-icon" />;
      default:
        return <FaHistory className="info-icon" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'in_progress':
        return 'warning';
      default:
        return 'info';
    }
  };

  const getMethodDisplayName = (method) => {
    const names = {
      'nist_800_88': 'NIST 800-88',
      'dod_5220_22_m': 'DoD 5220.22-M',
      'gutmann': 'Gutmann',
      'crypto_erase': 'Crypto Erase',
      'ata_sanitize': 'ATA Sanitize',
      'nvme_format': 'NVMe Format',
      'single_pass': 'Single Pass',
      'three_pass': 'Three Pass'
    };
    return names[method] || method;
  };

  if (loading) {
    return (
      <div className="card">
        <h2><FaFilePdf/> Wipe Reports</h2>
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading reports...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h2><FaFilePdf/> Wipe Reports</h2>
        <div className="error">
          <FaExclamationTriangle className="error-icon"/>
          <p>{error}</p>
          <button onClick={loadSessions} className="retry-button">
            <FaSyncAlt/> Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2><FaFilePdf/> Certificates & Reports</h2>
      <p>View and download tamper-proof certificates of data destruction for all wipe operations.</p>
      
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'sessions' ? 'active' : ''}`}
          onClick={() => setActiveTab('sessions')}
        >
          <FaHistory/> Wipe Sessions
        </button>
        <button 
          className={`tab-button ${activeTab === 'certificates' ? 'active' : ''}`}
          onClick={() => setActiveTab('certificates')}
        >
          <FaFilePdf/> Certificates
        </button>
      </div>

      {activeTab === 'sessions' ? (
        sessions.length === 0 ? (
          <div className="no-reports">
            <FaFilePdf className="no-reports-icon"/>
            <h3>No Wipe Sessions Found</h3>
            <p>No wipe operations have been performed yet. Start by wiping a device to generate reports.</p>
          </div>
        ) : (
        <div className="reports-table-container">
          <table className="reports-table">
            <thead>
              <tr>
                <th>Session ID</th>
                <th>Method</th>
                <th>Passes</th>
                <th>Status</th>
                <th>Started</th>
                <th>Duration</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((session) => (
                <tr key={session.id}>
                  <td className="session-id">#{session.id}</td>
                  <td className="method">
                    <span className="method-name">{getMethodDisplayName(session.method)}</span>
                  </td>
                  <td className="passes">{session.passes}</td>
                  <td className={`status status-${getStatusColor(session.status)}`}>
                    {getStatusIcon(session.status)}
                    <span>{session.status.replace('_', ' ').toUpperCase()}</span>
                  </td>
                  <td className="started">{formatDate(session.started_at)}</td>
                  <td className="duration">{formatDuration(session.duration_seconds)}</td>
                  <td className="actions">
                    {session.status === 'completed' && session.report_path && (
                      <div className="action-buttons">
                        <button 
                          onClick={() => downloadReport(session.id)}
                          className="download-button"
                          title="Download PDF Report"
                        >
                          <FaFilePdf/> PDF
                        </button>
                        <button 
                          onClick={() => downloadJsonReport(session.id)}
                          className="download-button"
                          title="Download JSON Certificate"
                        >
                          <FaFilePdf/> JSON
                        </button>
                        {session.signature_path && (
                          <button 
                            onClick={() => downloadSignature(session.id)}
                            className="download-button"
                            title="Download Signature"
                          >
                            <FaDownload/> Signature
                          </button>
                        )}
                      </div>
                    )}
                    {session.status === 'failed' && (
                      <span className="error-message">
                        {session.error_message || 'Unknown error'}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        )
      ) : (
        certificates.length === 0 ? (
          <div className="no-reports">
            <FaFilePdf className="no-reports-icon"/>
            <h3>No Certificates Found</h3>
            <p>No certificates have been generated yet. Complete a wipe operation to generate certificates.</p>
          </div>
        ) : (
          <div className="certificates-grid">
            {certificates.map((cert, index) => (
              <div key={index} className="certificate-card">
                <div className="certificate-header">
                  <div className="certificate-icon">
                    {cert.type === 'PDF' ? <FaFilePdf/> : <FaFilePdf/>}
                  </div>
                  <div className="certificate-info">
                    <h3>{cert.filename}</h3>
                    <p className="certificate-type">{cert.type} Certificate</p>
                  </div>
                </div>
                <div className="certificate-details">
                  <div className="detail-item">
                    <span className="label">Size:</span>
                    <span className="value">{formatSize(cert.size)}</span>
                  </div>
                  <div className="detail-item">
                    <span className="label">Created:</span>
                    <span className="value">{formatDate(cert.created)}</span>
                  </div>
                </div>
                <div className="certificate-actions">
                  <button 
                    onClick={() => viewCertificate(cert)}
                    className="view-button"
                  >
                    <FaFilePdf/> View
                  </button>
                  <button 
                    onClick={() => window.open(`/reports/${cert.filename}`, '_blank')}
                    className="download-button"
                  >
                    <FaDownload/> Download
                  </button>
                </div>
              </div>
            ))}
          </div>
        )
      )}

      <div className="reports-info">
        <h3>About Reports</h3>
        <ul>
          <li><strong>Reports:</strong> PDF certificates containing wipe details, timestamps, and verification hashes</li>
          <li><strong>Signatures:</strong> Digital signatures for tamper-proof verification of report authenticity</li>
          <li><strong>Compliance:</strong> Reports meet NIST 800-88 and DoD 5220.22-M standards for audit purposes</li>
        </ul>
      </div>

      <div className="button-group">
        <button onClick={onBack} className="secondary-button">
          ← Back
        </button>
        <button onClick={() => { loadSessions(); loadCertificates(); }} className="secondary-button">
          <FaSyncAlt/> Refresh
        </button>
      </div>
    </div>
  );
}

export default Reports;
