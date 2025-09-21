import React, { useState } from 'react';
import { FaDatabase, FaArrowRight } from 'react-icons/fa';

export default function DeviceList({ onNext }) {
  const [selected, setSelected] = useState([]);
  
  const devices = [
    { id: 'C:', name: 'C: (SSD 256GB)', size: '256GB' },
    { id: 'D:', name: 'D: (HDD 1TB)', size: '1TB' },
    { id: 'E:', name: 'E: (USB 32GB)', size: '32GB' }
  ];

  const toggleDevice = (deviceId) => {
    setSelected(prev => 
      prev.includes(deviceId) 
        ? prev.filter(id => id !== deviceId)
        : [...prev, deviceId]
    );
  };

  const handleNext = () => {
    const selectedDevices = devices.filter(d => selected.includes(d.id));
    onNext(selectedDevices);
  };

  return (
    <div className="card">
      <h2><FaDatabase/> Select Devices to Wipe</h2>
      <div style={{ marginBottom: '16px' }}>
        {devices.map(device => (
          <label key={device.id} style={{ display: 'block', marginBottom: '8px', cursor: 'pointer' }}>
            <input 
              type="checkbox" 
              checked={selected.includes(device.id)}
              onChange={() => toggleDevice(device.id)}
              style={{ marginRight: '8px' }}
            />
            {device.name} ({device.size})
          </label>
        ))}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <button onClick={() => window.location.reload()}>Refresh</button>
        <button 
          onClick={handleNext} 
          disabled={selected.length === 0}
          style={{ 
            background: selected.length === 0 ? '#ccc' : '#0b66c3',
            cursor: selected.length === 0 ? 'not-allowed' : 'pointer'
          }}
        >
          Next <FaArrowRight/>
        </button>
      </div>
    </div>
  );
}
