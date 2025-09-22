import React, { useState, useEffect } from 'react';
import { FaFilePdf, FaDownload, FaShieldAlt, FaCheckCircle, FaTimesCircle, FaArrowLeft, FaEye, FaCode } from 'react-icons/fa';

const API_BASE_URL = '/api';
const BACKEND_BASE_URL = '';

function CertificateViewer({ certificate, onBack }) {
  const [certificateData, setCertificateData] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [viewMode, setViewMode] = useState('formatted'); // 'formatted' or 'raw'

  useEffect(() => {
    if (certificate) {
      loadCertificateData();
    }
  }, [certificate]);

  const loadCertificateData = async () => {
    if (!certificate) return;

    setLoading(true);
    setError('');

    try {
      if (certificate.type === 'JSON') {
        // Load JSON certificate
        const response = await fetch(`${API_BASE_URL}/reports/${certificate.sessionId}/json`);
        if (response.ok) {
          const data = await response.json();
          setCertificateData(data);
        } else {
          throw new Error('Failed to load JSON certificate');
        }
      } else {
        // For PDF certificates, we'll show basic info
        setCertificateData({
          certificate: {
            id: certificate.id || 'N/A',
            issued_at: certificate.created || new Date().toISOString(),
            type: 'PDF Certificate'
          },
          device: {
            path: certificate.devicePath || 'N/A',
            type: certificate.deviceType || 'N/A'
          },
          wipe_operation: {
            method: certificate.method || 'N/A',
            status: certificate.status || 'N/A',
            started_at: certificate.startedAt || 'N/A',
            completed_at: certificate.completedAt || 'N/A'
          }
        });
      }
    } catch (err) {
      setError('Failed to load certificate data');
      console.error('Error loading certificate:', err);
    } finally {
      setLoading(false);
    }
  };

  const verifyCertificate = async () => {
    if (!certificate) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/reports/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file_path: certificate.path
        })
      });

      const result = await response.json();
      setVerificationResult(result);
    } catch (err) {
      setVerificationResult({ valid: false, error: 'Verification failed' });
    } finally {
      setLoading(false);
    }
  };

  const downloadCertificate = () => {
    if (!certificate) return;

    const url = certificate.type === 'JSON' 
      ? `${API_BASE_URL}/reports/${certificate.sessionId}/json`
      : `${API_BASE_URL}/reports/${certificate.sessionId}`;
    
    window.open(url, '_blank');
  };

  const downloadSignature = () => {
    if (!certificate) return;
    
    const url = `${API_BASE_URL}/reports/${certificate.sessionId}/signature`;
    window.open(url, '_blank');
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const formatSize = (bytes) => {
    if (!bytes) return 'N/A';
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  };

  if (loading) {
    return (
      <div className="card">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading certificate...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="error">
          <FaTimesCircle className="error-icon"/>
          <h3>Error Loading Certificate</h3>
          <p>{error}</p>
          <button onClick={onBack} className="primary-button">
            <FaArrowLeft/> Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card certificate-viewer">
      <div className="certificate-header">
        <div className="header-left">
          <button onClick={onBack} className="back-button">
            <FaArrowLeft/> Back
          </button>
          <h2>
            <FaShieldAlt className="certificate-icon"/>
            Certificate Viewer
          </h2>
        </div>
        <div className="header-right">
          <div className="view-mode-toggle">
            <button 
              className={viewMode === 'formatted' ? 'active' : ''}
              onClick={() => setViewMode('formatted')}
              title="Formatted View"
            >
              <FaEye/> Formatted
            </button>
            <button 
              className={viewMode === 'raw' ? 'active' : ''}
              onClick={() => setViewMode('raw')}
              title="Raw JSON View"
            >
              <FaCode/> Raw
            </button>
          </div>
          <div className="action-buttons">
            <button onClick={verifyCertificate} className="secondary-button">
              <FaShieldAlt/> Verify
            </button>
            <button onClick={downloadCertificate} className="primary-button">
              <FaDownload/> Download
            </button>
          </div>
        </div>
      </div>

      {verificationResult && (
        <div className={`verification-result ${verificationResult.valid ? 'valid' : 'invalid'}`}>
          {verificationResult.valid ? (
            <>
              <FaCheckCircle className="success-icon"/>
              <span>Certificate is authentic and untampered</span>
            </>
          ) : (
            <>
              <FaTimesCircle className="error-icon"/>
              <span>Certificate verification failed: {verificationResult.error}</span>
            </>
          )}
        </div>
      )}

      {viewMode === 'formatted' ? (
        <div className="certificate-content">
          {certificateData && (
            <>
              {/* Certificate Info */}
              <div className="certificate-section">
                <h3>Certificate Information</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <label>Certificate ID:</label>
                    <span className="certificate-id">{certificateData.certificate?.id || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <label>Type:</label>
                    <span>{certificateData.certificate?.type || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <label>Issued:</label>
                    <span>{formatDate(certificateData.certificate?.issued_at)}</span>
                  </div>
                  <div className="info-item">
                    <label>Status:</label>
                    <span className={`status ${certificateData.certificate?.status || 'unknown'}`}>
                      {certificateData.certificate?.status || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Device Information */}
              <div className="certificate-section">
                <h3>Device Information</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <label>Device Path:</label>
                    <span className="device-path">{certificateData.device?.path || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <label>Device Type:</label>
                    <span className="device-type">{certificateData.device?.type?.toUpperCase() || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <label>Model:</label>
                    <span>{certificateData.device?.model || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <label>Serial Number:</label>
                    <span>{certificateData.device?.serial || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <label>Size:</label>
                    <span>{certificateData.device?.size_formatted || formatSize(certificateData.device?.size_bytes)}</span>
                  </div>
                </div>
              </div>

              {/* Wipe Operation */}
              <div className="certificate-section">
                <h3>Wipe Operation Details</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <label>Method:</label>
                    <span className="wipe-method">{certificateData.wipe_operation?.method_display || certificateData.wipe_operation?.method || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <label>Passes:</label>
                    <span>{certificateData.wipe_operation?.passes || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <label>Started:</label>
                    <span>{formatDate(certificateData.wipe_operation?.started_at)}</span>
                  </div>
                  <div className="info-item">
                    <label>Completed:</label>
                    <span>{formatDate(certificateData.wipe_operation?.completed_at)}</span>
                  </div>
                  <div className="info-item">
                    <label>Duration:</label>
                    <span>{certificateData.wipe_operation?.duration_formatted || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <label>Status:</label>
                    <span className={`status ${certificateData.wipe_operation?.status || 'unknown'}`}>
                      {certificateData.wipe_operation?.status?.toUpperCase() || 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Verification Data */}
              {certificateData.verification && (
                <div className="certificate-section">
                  <h3>Verification Data</h3>
                  <div className="info-grid">
                    <div className="info-item">
                      <label>SHA-256 Before:</label>
                      <span className="hash-value">{certificateData.verification.sha256_before || 'N/A'}</span>
                    </div>
                    <div className="info-item">
                      <label>SHA-256 After:</label>
                      <span className="hash-value">{certificateData.verification.sha256_after || 'N/A'}</span>
                    </div>
                    <div className="info-item">
                      <label>Data Destroyed:</label>
                      <span className={`verification-status ${certificateData.verification.data_destroyed ? 'success' : 'error'}`}>
                        {certificateData.verification.data_destroyed ? '✅ YES' : '❌ NO'}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Digital Signature */}
              {certificateData.digital_signature && (
                <div className="certificate-section">
                  <h3>Digital Signature</h3>
                  <div className="info-grid">
                    <div className="info-item">
                      <label>Algorithm:</label>
                      <span>{certificateData.digital_signature.algorithm || 'N/A'}</span>
                    </div>
                    <div className="info-item">
                      <label>Signature Hash:</label>
                      <span className="hash-value">{certificateData.digital_signature.signature_hash || 'N/A'}</span>
                    </div>
                    <div className="info-item">
                      <label>Public Key Fingerprint:</label>
                      <span className="hash-value">{certificateData.digital_signature.public_key_fingerprint || 'N/A'}</span>
                    </div>
                    <div className="info-item">
                      <label>Tamper Proof:</label>
                      <span className={`verification-status ${certificateData.digital_signature.tamper_proof ? 'success' : 'error'}`}>
                        {certificateData.digital_signature.tamper_proof ? '✅ YES' : '❌ NO'}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Compliance */}
              {certificateData.compliance && (
                <div className="certificate-section">
                  <h3>Compliance Standards</h3>
                  <div className="compliance-badges">
                    {certificateData.compliance.standards_met?.map((standard, index) => (
                      <span key={index} className="compliance-badge">
                        {standard}
                      </span>
                    )) || <span>N/A</span>}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      ) : (
        <div className="raw-json-viewer">
          <pre>{JSON.stringify(certificateData, null, 2)}</pre>
        </div>
      )}

      <div className="certificate-footer">
        <div className="footer-info">
          <span>Generated by ZeroTrace v1.0.0</span>
          <span>•</span>
          <span>Tamper-Proof Certificate</span>
        </div>
        <div className="footer-actions">
          <button onClick={downloadSignature} className="secondary-button">
            <FaDownload/> Signature
          </button>
        </div>
      </div>
    </div>
  );
}

export default CertificateViewer;
