import React, { useState, useEffect } from 'react';
import { FaSpinner, FaCheckCircle, FaExclamationTriangle, FaTimesCircle } from 'react-icons/fa';

function WipeProgress({ selectedDevices, method, passes, progress, status, error, onBack }) {
  const [startTime] = useState(Date.now());
  const [elapsedTime, setElapsedTime] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    return () => clearInterval(interval);
  }, [startTime]);

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const getStatusIcon = () => {
    if (error) return <FaTimesCircle className="error-icon" />;
    if (progress >= 100) return <FaCheckCircle className="success-icon" />;
    return <FaSpinner className="spinning-icon" />;
  };

  const getStatusColor = () => {
    if (error) return 'error';
    if (progress >= 100) return 'success';
    return 'in-progress';
  };

  const getMethodDisplayName = (method) => {
    const names = {
      'nist_800_88': 'NIST 800-88',
      'dod_5220_22_m': 'DoD 5220.22-M',
      'gutmann': 'Gutmann (35-pass)',
      'crypto_erase': 'Cryptographic Erase',
      'ata_sanitize': 'ATA Sanitize',
      'nvme_format': 'NVMe Format',
      'single_pass': 'Single Pass',
      'three_pass': 'Three Pass'
    };
    return names[method] || method;
  };

  return (
    <div className="card">
      <h2>Wipe Progress</h2>
      
      <div className="progress-header">
        <div className="device-info">
          <h3>Wiping Device:</h3>
          <p><strong>{selectedDevices[0]?.name || selectedDevices[0]?.model || 'Unknown'}</strong></p>
          <p className="device-path">{selectedDevices[0]?.path}</p>
        </div>
        
        <div className="method-info">
          <h3>Method:</h3>
          <p><strong>{getMethodDisplayName(method)}</strong></p>
          {passes > 1 && <p>Passes: {passes}</p>}
        </div>
      </div>

      <div className={`progress-container ${getStatusColor()}`}>
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ width: `${Math.min(progress, 100)}%` }}
          ></div>
        </div>
        <div className="progress-text">
          <span className="progress-percentage">{Math.round(progress)}%</span>
          <span className="progress-status">{status}</span>
        </div>
      </div>

      <div className="progress-details">
        <div className="detail-item">
          <span className="detail-label">Elapsed Time:</span>
          <span className="detail-value">{formatTime(elapsedTime)}</span>
        </div>
        
        <div className="detail-item">
          <span className="detail-label">Status:</span>
          <span className={`detail-value status-${getStatusColor()}`}>
            {getStatusIcon()}
            {error ? 'Failed' : progress >= 100 ? 'Completed' : 'In Progress'}
          </span>
        </div>

        {progress > 0 && progress < 100 && (
          <div className="detail-item">
            <span className="detail-label">Estimated Remaining:</span>
            <span className="detail-value">
              {elapsedTime > 0 ? formatTime(Math.floor((elapsedTime / progress) * (100 - progress))) : 'Calculating...'}
            </span>
          </div>
        )}
      </div>

      {error && (
        <div className="error-section">
          <FaExclamationTriangle className="error-icon" />
          <div className="error-content">
            <h3>Wipe Failed</h3>
            <p className="error-message">{error}</p>
            <p>Please check the device connection and try again.</p>
          </div>
        </div>
      )}

      {progress >= 100 && !error && (
        <div className="success-section">
          <FaCheckCircle className="success-icon" />
          <div className="success-content">
            <h3>Wipe Completed Successfully!</h3>
            <p>Your data has been securely erased using {getMethodDisplayName(method)} method.</p>
            <p>Total time: {formatTime(elapsedTime)}</p>
          </div>
        </div>
      )}

      <div className="progress-warning">
        <FaExclamationTriangle className="warning-icon" />
        <p>
          <strong>Important:</strong> Do not disconnect the device or close this application 
          during the wipe process. This could result in data corruption or incomplete wiping.
        </p>
      </div>

      <div className="button-group">
        {!error && progress < 100 && (
          <button onClick={onBack} className="secondary-button" disabled>
            ← Back (Disabled during wipe)
          </button>
        )}
        
        {(error || progress >= 100) && (
          <button onClick={onBack} className="primary-button">
            ← Back
          </button>
        )}
      </div>
    </div>
  );
}

export default WipeProgress;
