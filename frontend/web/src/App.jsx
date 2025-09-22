import React, { useState, useEffect } from 'react';
import DeviceList from './components/DeviceList';
import WipeOptions from './components/WipeOptions';
import WipeProgress from './components/WipeProgress';
import Reports from './components/Reports';
import CertificateViewer from './components/CertificateViewer';
import { FaHome, FaDatabase, FaFilePdf, FaCog, FaHistory, FaMoon, FaSun, FaShieldAlt } from 'react-icons/fa';
import './App.css';

const API_BASE_URL = '/api';

function Home() {
  return (
    <div className="card">
      <h2><FaHome/> Welcome to ZeroTrace</h2>
      <div className="welcome-content">
        <p>ZeroTrace is a secure data wiping tool that ensures your sensitive data is permanently erased using industry-standard methods.</p>
        <div className="features">
          <h3>Features:</h3>
          <ul>
            <li>✅ NIST 800-88 compliant wiping</li>
            <li>✅ DoD 5220.22-M standard</li>
            <li>✅ Cryptographic erasure for SSDs</li>
            <li>✅ Real-time progress tracking</li>
            <li>✅ Digital certificates and reports</li>
            <li>✅ Cross-platform support</li>
          </ul>
        </div>
        <div className="security-note">
          <strong>⚠️ Warning:</strong> This tool permanently destroys data. Use with extreme caution.
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [step, setStep] = useState('home');
  const [selectedDevices, setSelectedDevices] = useState([]);
  const [wipeMethod, setWipeMethod] = useState('');
  const [wipePasses, setWipePasses] = useState(1);
  const [currentSession, setCurrentSession] = useState(null);
  const [wipeProgress, setWipeProgress] = useState(0);
  const [wipeStatus, setWipeStatus] = useState('');
  const [wipeError, setWipeError] = useState('');
  const [availableMethods, setAvailableMethods] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [selectedCertificate, setSelectedCertificate] = useState(null);

  // Load available wipe methods on component mount
  useEffect(() => {
    loadWipeMethods();
  }, []);

  const loadWipeMethods = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/wipe/methods`);
      const data = await response.json();
      setAvailableMethods(data.methods);
    } catch (error) {
      console.error('Failed to load wipe methods:', error);
    }
  };

  const handleDeviceSelection = (devices) => {
    setSelectedDevices(devices);
    setStep('options');
  };

  const handleWipeStart = async (method, passes) => {
    if (selectedDevices.length === 0) {
      alert('Please select at least one device');
      return;
    }

    setIsLoading(true);
    setWipeMethod(method);
    setWipePasses(passes);
    setStep('progress');
    setWipeProgress(0);
    setWipeStatus('Starting wipe...');
    setWipeError('');

    try {
      // Start wipe for the first selected device
      const device = selectedDevices[0];
      const response = await fetch(`${API_BASE_URL}/wipe`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          device: device.path,
          method: method,
          passes: passes,
          force: true
        })
      });

      const result = await response.json();
      
      if (result.result.success) {
        setCurrentSession(result.result.session_id);
        // Start polling for progress
        pollProgress(result.result.session_id);
      } else {
        setWipeError(result.result.error || 'Wipe failed');
        setWipeStatus('Failed');
      }
    } catch (error) {
      setWipeError(error.message);
      setWipeStatus('Failed');
    } finally {
      setIsLoading(false);
    }
  };

  const pollProgress = async (sessionId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/wipe/${sessionId}/progress`);
        const progress = await response.json();
        
        setWipeProgress(progress.progress_percentage);
        setWipeStatus(progress.status_message);

        if (progress.progress_percentage >= 100) {
          clearInterval(pollInterval);
          setWipeStatus('Wipe completed successfully!');
          setTimeout(() => setStep('complete'), 2000);
        }
      } catch (error) {
        console.error('Failed to get progress:', error);
        clearInterval(pollInterval);
        setWipeError('Failed to get progress updates');
        setWipeStatus('Error');
      }
    }, 1000);
  };

  const handleBack = () => {
    if (step === 'options') {
      setStep('devices');
    } else if (step === 'progress') {
      setStep('options');
    } else if (step === 'complete') {
      setStep('devices');
    } else if (step === 'reports') {
      setStep('home');
    } else if (step === 'certificate') {
      setStep('reports');
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  const handleViewCertificate = (certificate) => {
    setSelectedCertificate(certificate);
    setStep('certificate');
  };

  return (
    <div className={`app ${darkMode ? 'dark-mode' : ''}`}>
      <header className="app-header">
        <div className="header-left">
          <h1><FaShieldAlt/> ZeroTrace</h1>
          <span className="subtitle">Secure Data Wiping</span>
        </div>
        <div className="header-right">
          <nav className="nav-buttons">
            <button 
              className={step === 'home' ? 'active' : ''} 
              onClick={() => setStep('home')}
              title="Home"
            >
              <FaHome/> Home
            </button>
            <button 
              className={step === 'devices' ? 'active' : ''} 
              onClick={() => setStep('devices')}
              title="Devices"
            >
              <FaDatabase/> Devices
            </button>
            <button 
              className={step === 'reports' ? 'active' : ''} 
              onClick={() => setStep('reports')}
              title="Certificates"
            >
              <FaFilePdf/> Certificates
            </button>
          </nav>
          <button 
            className="theme-toggle"
            onClick={toggleDarkMode}
            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {darkMode ? <FaSun/> : <FaMoon/>}
          </button>
        </div>
      </header>
      
      <main className="app-main">
        {step === 'home' && <Home />}
        {step === 'devices' && (
          <DeviceList 
            onNext={handleDeviceSelection}
            onBack={() => setStep('home')}
          />
        )}
        {step === 'options' && (
          <WipeOptions
            selectedDevices={selectedDevices}
            availableMethods={availableMethods}
            onStart={handleWipeStart}
            onBack={handleBack}
            isLoading={isLoading}
          />
        )}
        {step === 'progress' && (
          <WipeProgress
            selectedDevices={selectedDevices}
            method={wipeMethod}
            passes={wipePasses}
            progress={wipeProgress}
            status={wipeStatus}
            error={wipeError}
            onBack={handleBack}
          />
        )}
        {step === 'complete' && (
          <div className="card">
            <h2>✅ Wipe Complete</h2>
            <p>Your data has been securely wiped using {wipeMethod} method.</p>
            <div className="button-group">
              <button onClick={() => setStep('reports')}>
                <FaFilePdf/> View Reports
              </button>
              <button onClick={() => setStep('devices')}>
                <FaDatabase/> Wipe Another Device
              </button>
            </div>
          </div>
        )}
        {step === 'reports' && (
          <Reports onBack={handleBack} onViewCertificate={handleViewCertificate} />
        )}
        {step === 'certificate' && (
          <CertificateViewer 
            certificate={selectedCertificate} 
            onBack={handleBack} 
          />
        )}
      </main>
    </div>
  );
}
