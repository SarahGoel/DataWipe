import React, { useState, useEffect } from 'react';
import { FaDatabase, FaSyncAlt, FaExclamationTriangle } from 'react-icons/fa';

const API_BASE_URL = '/api';

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
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 8000);
      const response = await fetch(`${API_BASE_URL}/drives`, { signal: controller.signal });
      clearTimeout(timeoutId);
      let data = null;
      try {
        data = await response.json();
      } catch (e) {
        data = null;
      }
      
      if (data && data.ok) {
        const list = Array.isArray(data.drives) ? data.drives : [];
        if (list.length === 0) {
          setDevices([
            { name: 'Primary Drive', path: 'demo://drive0', type: 'ssd', size: String(256 * 1024 * 1024 * 1024) }
          ]);
        } else {
          setDevices(list);
        }
      } else if (data && data.drives && Array.isArray(data.drives)) {
        const list = data.drives;
        setDevices(list.length > 0 ? list : [
          { name: 'Primary Drive', path: 'demo://drive0', type: 'ssd', size: String(256 * 1024 * 1024 * 1024) }
        ]);
      } else if (response.ok) {
        setDevices([
          { name: 'Primary Drive', path: 'demo://drive0', type: 'ssd', size: String(256 * 1024 * 1024 * 1024) }
        ]);
      } else {
        setError((data && data.error) ? data.error : 'Failed to load devices');
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
            <FaSyncAlt/> Retry
          </button>
        </div>
      </div>
    );
  }

  // Sanitize devices before rendering to prevent crashes on unexpected shapes
  const sanitizedDevices = (devices || []).filter(Boolean).map((device) => ({
    name: device?.name || device?.model || 'Unknown Device',
    path: device?.path || 'demo://drive0',
    type: (typeof device?.type === 'string' && device.type) ? device.type : 'unknown',
    size: device?.size || device?.size_bytes || '0',
    model: device?.model || '',
    serial: device?.serial || device?.serial_number || '',
    is_removable: Boolean(device?.is_removable),
  }));

  return (
    <div className="card">
      <h2><FaDatabase/> Available Devices</h2>
      <p>Select the devices you want to securely wipe. <strong>Warning: This will permanently destroy all data!</strong></p>
      {(sanitizedDevices.length === 0) && (
        <div className="no-devices">
          <p>No devices found yet. This could be due to limited permissions or a blocked enumeration command. You can still proceed with demo mode.</p>
            <button onClick={loadDevices} className="refresh-button">
            <FaSyncAlt/> Try Again
          </button>
        </div>
      )}
      
      <div className="device-list">
        {sanitizedDevices.length > 0 && (
          sanitizedDevices.map((device, index) => (
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
                  <span className="device-type">{(device.type || 'UNKNOWN').toUpperCase()}</span>
                  <span className="device-size">{formatSize(device.size)}</span>
                  {device.is_removable ? <span className="removable">Removable</span> : null}
                </div>
                {device.serial ? (
                  <p className="device-serial">Serial: {device.serial}</p>
                ) : null}
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
          <FaSyncAlt/> Refresh
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
