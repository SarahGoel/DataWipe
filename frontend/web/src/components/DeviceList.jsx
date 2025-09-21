import React, { useState, useEffect } from 'react';
import { FaDatabase, FaRefresh, FaExclamationTriangle } from 'react-icons/fa';

const API_BASE_URL = 'http://localhost:8000/api';

function DeviceList({ onNext, onBack }) {
  const [devices, setDevices] = useState([]);
  const [selectedDevices, setSelectedDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDevices();
  }, []);

  const loadDevices = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await fetch(`${API_BASE_URL}/drives`);
      const data = await response.json();
      
      if (data.ok) {
        setDevices(data.drives || []);
      } else {
        setError(data.error || 'Failed to load devices');
      }
    } catch (err) {
      setError('Failed to connect to backend');
      console.error('Error loading devices:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeviceSelect = (device) => {
    setSelectedDevices(prev => {
      if (prev.find(d => d.path === device.path)) {
        return prev.filter(d => d.path !== device.path);
      } else {
        return [...prev, device];
      }
    });
  };

  const handleNext = () => {
    if (selectedDevices.length === 0) {
      alert('Please select at least one device to wipe');
      return;
    }
    onNext(selectedDevices);
  };

  const formatSize = (sizeStr) => {
    if (!sizeStr) return 'Unknown';
    const size = parseInt(sizeStr);
    if (isNaN(size)) return sizeStr;
    
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let unitIndex = 0;
    let sizeValue = size;
    
    while (sizeValue >= 1024 && unitIndex < units.length - 1) {
      sizeValue /= 1024;
      unitIndex++;
    }
    
    return `${sizeValue.toFixed(1)} ${units[unitIndex]}`;
  };

  const getDeviceIcon = (device) => {
    if (device.type === 'ssd') return '💾';
    if (device.type === 'hdd') return '💿';
    if (device.type === 'nvme') return '⚡';
    if (device.is_removable) return '🔌';
    return '💽';
  };

  if (loading) {
    return (
      <div className="card">
        <h2><FaDatabase/> Available Devices</h2>
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading devices...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <h2><FaDatabase/> Available Devices</h2>
        <div className="error">
          <FaExclamationTriangle className="error-icon"/>
          <p>{error}</p>
          <button onClick={loadDevices} className="retry-button">
            <FaRefresh/> Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h2><FaDatabase/> Available Devices</h2>
      <p>Select the devices you want to securely wipe. <strong>Warning: This will permanently destroy all data!</strong></p>
      
      <div className="device-list">
        {devices.length === 0 ? (
          <div className="no-devices">
            <p>No devices found. Make sure your storage devices are connected.</p>
            <button onClick={loadDevices} className="refresh-button">
              <FaRefresh/> Refresh
            </button>
          </div>
        ) : (
          devices.map((device, index) => (
            <div 
              key={index}
              className={`device-item ${selectedDevices.find(d => d.path === device.path) ? 'selected' : ''}`}
              onClick={() => handleDeviceSelect(device)}
            >
              <div className="device-icon">
                {getDeviceIcon(device)}
              </div>
              <div className="device-info">
                <h3>{device.name || device.model || 'Unknown Device'}</h3>
                <p className="device-path">{device.path}</p>
                <div className="device-details">
                  <span className="device-type">{device.type?.toUpperCase() || 'UNKNOWN'}</span>
                  <span className="device-size">{formatSize(device.size)}</span>
                  {device.is_removable && <span className="removable">Removable</span>}
                </div>
                {device.serial && (
                  <p className="device-serial">Serial: {device.serial}</p>
                )}
              </div>
              <div className="device-select">
                <input 
                  type="checkbox" 
                  checked={selectedDevices.find(d => d.path === device.path) ? true : false}
                  onChange={() => handleDeviceSelect(device)}
                />
              </div>
            </div>
          ))
        )}
      </div>

      <div className="selected-summary">
        {selectedDevices.length > 0 && (
          <p><strong>{selectedDevices.length}</strong> device(s) selected</p>
        )}
      </div>

      <div className="button-group">
        <button onClick={onBack} className="secondary-button">
          ← Back
        </button>
        <button onClick={loadDevices} className="secondary-button">
          <FaRefresh/> Refresh
        </button>
        <button 
          onClick={handleNext} 
          className="primary-button"
          disabled={selectedDevices.length === 0}
        >
          Next: Choose Method →
        </button>
      </div>
    </div>
  );
}

export default DeviceList;
