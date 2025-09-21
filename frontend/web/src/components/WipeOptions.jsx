import React, { useState } from 'react';
import { FaCog, FaExclamationTriangle, FaInfoCircle } from 'react-icons/fa';

function WipeOptions({ selectedDevices, availableMethods, onStart, onBack, isLoading }) {
  const [selectedMethod, setSelectedMethod] = useState('');
  const [passes, setPasses] = useState(1);
  const [confirmWipe, setConfirmWipe] = useState(false);

  const handleStart = () => {
    if (!selectedMethod) {
      alert('Please select a wipe method');
      return;
    }
    if (!confirmWipe) {
      alert('Please confirm that you understand this will permanently destroy data');
      return;
    }
    onStart(selectedMethod, passes);
  };

  const getMethodInfo = (method) => {
    const info = {
      'nist_800_88': {
        name: 'NIST 800-88',
        description: 'Industry standard: Clear + Verify + Purge',
        recommended: true,
        time: 'Medium'
      },
      'dod_5220_22_m': {
        name: 'DoD 5220.22-M',
        description: 'Military standard: 3-pass overwrite',
        recommended: true,
        time: 'Medium'
      },
      'gutmann': {
        name: 'Gutmann',
        description: 'Maximum security: 35-pass overwrite',
        recommended: false,
        time: 'Very Long'
      },
      'crypto_erase': {
        name: 'Cryptographic Erase',
        description: 'Preferred for SSDs: Key destruction',
        recommended: true,
        time: 'Fast'
      },
      'ata_sanitize': {
        name: 'ATA Sanitize',
        description: 'Hardware-level secure erase',
        recommended: true,
        time: 'Fast'
      },
      'nvme_format': {
        name: 'NVMe Format',
        description: 'NVMe crypto erase command',
        recommended: true,
        time: 'Fast'
      },
      'single_pass': {
        name: 'Single Pass',
        description: 'Quick wipe with zeros',
        recommended: false,
        time: 'Fast'
      },
      'three_pass': {
        name: 'Three Pass',
        description: 'Zeros, ones, and random data',
        recommended: false,
        time: 'Medium'
      }
    };
    return info[method] || { name: method, description: 'Unknown method', recommended: false, time: 'Unknown' };
  };

  const getRecommendedMethod = () => {
    // Recommend crypto erase for SSDs, NIST for others
    const hasSSD = selectedDevices.some(device => device.type === 'ssd' || device.type === 'nvme');
    return hasSSD ? 'crypto_erase' : 'nist_800_88';
  };

  React.useEffect(() => {
    if (availableMethods.length > 0 && !selectedMethod) {
      setSelectedMethod(getRecommendedMethod());
    }
  }, [availableMethods, selectedMethod]);

  return (
    <div className="card">
      <h2><FaCog/> Wipe Options</h2>
      
      <div className="selected-devices-summary">
        <h3>Selected Devices:</h3>
        <ul>
          {selectedDevices.map((device, index) => (
            <li key={index}>
              <strong>{device.name || device.model || 'Unknown'}</strong> 
              ({device.path}) - {device.type?.toUpperCase() || 'UNKNOWN'}
            </li>
          ))}
        </ul>
      </div>

      <div className="wipe-method-selection">
        <h3>Choose Wipe Method:</h3>
        <div className="method-grid">
          {availableMethods.map((method) => {
            const info = getMethodInfo(method.id);
            return (
              <div 
                key={method.id}
                className={`method-option ${selectedMethod === method.id ? 'selected' : ''} ${info.recommended ? 'recommended' : ''}`}
                onClick={() => setSelectedMethod(method.id)}
              >
                <div className="method-header">
                  <input 
                    type="radio" 
                    name="method" 
                    value={method.id}
                    checked={selectedMethod === method.id}
                    onChange={() => setSelectedMethod(method.id)}
                  />
                  <h4>{info.name}</h4>
                  {info.recommended && <span className="recommended-badge">Recommended</span>}
                </div>
                <p className="method-description">{info.description}</p>
                <div className="method-details">
                  <span className="time-estimate">⏱️ {info.time}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {selectedMethod && (
        <div className="method-settings">
          <h3>Method Settings:</h3>
          
          {['dod_5220_22_m', 'three_pass', 'gutmann'].includes(selectedMethod) && (
            <div className="setting-group">
              <label htmlFor="passes">Number of Passes:</label>
              <select 
                id="passes" 
                value={passes} 
                onChange={(e) => setPasses(parseInt(e.target.value))}
              >
                <option value={1}>1 Pass</option>
                <option value={3}>3 Passes</option>
                {selectedMethod === 'gutmann' && <option value={35}>35 Passes (Gutmann)</option>}
              </select>
            </div>
          )}

          <div className="method-info">
            <FaInfoCircle className="info-icon"/>
            <div>
              <strong>Method Details:</strong>
              <p>{getMethodInfo(selectedMethod).description}</p>
              {selectedMethod === 'crypto_erase' && (
                <p className="crypto-note">
                  <strong>Note:</strong> Cryptographic erasure is the fastest and most secure method for SSDs. 
                  It destroys the encryption keys, making data recovery impossible.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="warning-section">
        <FaExclamationTriangle className="warning-icon"/>
        <div className="warning-content">
          <h3>⚠️ DANGER: Data Destruction Warning</h3>
          <ul>
            <li>This operation will <strong>PERMANENTLY DESTROY</strong> all data on the selected devices</li>
            <li>Data recovery will be <strong>IMPOSSIBLE</strong> after this operation</li>
            <li>Make sure you have backed up any important data</li>
            <li>Double-check that you have selected the correct devices</li>
          </ul>
        </div>
      </div>

      <div className="confirmation-section">
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            checked={confirmWipe}
            onChange={(e) => setConfirmWipe(e.target.checked)}
          />
          <span>I understand that this will permanently destroy all data and I have backed up any important information</span>
        </label>
      </div>

      <div className="button-group">
        <button onClick={onBack} className="secondary-button" disabled={isLoading}>
          ← Back
        </button>
        <button 
          onClick={handleStart} 
          className="danger-button"
          disabled={!selectedMethod || !confirmWipe || isLoading}
        >
          {isLoading ? 'Starting...' : '🚨 START SECURE WIPE 🚨'}
        </button>
      </div>
    </div>
  );
}

export default WipeOptions;
