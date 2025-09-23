# 🔐 ZeroTrace – Secure Data Wiping Tool

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![React](https://img.shields.io/badge/React-18+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green)
![NIST](https://img.shields.io/badge/NIST-800--88-compliant-orange)

ZeroTrace is a secure data wiping tool with a FastAPI backend and a modern React (Vite) frontend. It generates tamper‑proof wipe certificates and includes an Electron desktop shell for presentations.

## ⚡ Quick Start

- Run from the repo root to install deps, build the web app, and start the API that serves the built UI at /:
```powershell
# Windows (PowerShell)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pushd frontend/web; npm install; npm run build; popd
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
```bash
# macOS/Linux (bash)
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
pushd frontend/web && npm install && npm run build && popd
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
App: http://127.0.0.1:8000 • API docs: http://127.0.0.1:8000/docs

- Safe wipe demo (generates certificate):
```powershell
$demo = "$env:TEMP\zerotrace_demo.txt"
'Demo content' | Out-File -Encoding utf8 $demo
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/wipe-file -ContentType application/json -Body (@{ path = $demo; passes = 1; force = $true } | ConvertTo-Json)
```
Then open Certificates in the app.

## 🧑‍💻 Manual Setup (if needed)

- Backend deps:
```powershell
cd backend
python -m pip install -r ..\requirements.txt
```
- Frontend build (Vite ESM config at `frontend/web/vite.config.mjs`):
```powershell
cd frontend\web
npm install
npm run build
```
- Run backend (serves built web at /):
```powershell
cd ..\..\backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

- Electron desktop window (dev, optional):
```powershell
cd frontend\web
npm run dev
npm run electron
```

---

## 🚀 Features

### 🔒 Security Standards
- **NIST 800-88 Compliant**: Industry-standard Clear + Verify + Purge process
- **DoD 5220.22-M**: Military-grade 3-pass secure erase
- **Gutmann Method**: 35-pass maximum security overwrite
- **Cryptographic Erasure**: Key destruction for SSDs (preferred method)
- **ATA Sanitize**: Hardware-level secure erase commands
- **NVMe Format**: Crypto erase for NVMe SSDs

### 💻 Cross-Platform Support
- **Windows**: PowerShell-based device detection and wiping
- **Linux**: Native tools (lsblk, hdparm, nvme-cli, dd)
- **macOS**: system_profiler integration
- **Device Types**: HDD, SSD, NVMe, USB drives

### 📊 Advanced Features
- **Real-time Progress**: Live progress tracking with time estimates
- **Tamper-proof Certificates**: PDF and JSON certificates with digital signatures
- **Certificate Viewer**: Interactive certificate display and verification
- **Audit Logging**: Comprehensive activity logging for compliance
- **Device Detection**: Automatic device type detection and information gathering
- **Error Handling**: Robust error recovery and user feedback
- **Dark Mode**: Modern UI with light/dark theme support

### 🎨 Modern Interface
- **React Frontend**: Responsive, modern web interface with Vite
- **FastAPI Backend**: High-performance async API with automatic documentation
- **Real-time Updates**: Live progress tracking and status updates
- **Mobile Friendly**: Responsive design for all devices
- **Professional UI**: Polished interface with animations and transitions


## ⚙️ Installation & Setup

### Prerequisites

- Python 3.9+ and Node.js 18+ (LTS recommended). If missing, install via:
  - Windows: `winget install -e --id Python.Python.3` and `winget install -e --id OpenJS.NodeJS.LTS`
  - macOS: `brew install python node`
  - Ubuntu/Debian: `sudo apt update && sudo apt install -y python3 python3-pip nodejs npm`
  - Fedora: `sudo dnf install -y python3 python3-pip nodejs`
  - Arch: `sudo pacman -S --noconfirm python nodejs npm`

Notes for secure wipe tooling (optional, OS-native binaries):
- Linux: `sudo apt install -y hdparm nvme-cli` (or distro equivalents)
- macOS: uses system tools; run Terminal as admin and unmount target disks if needed
- Windows: run PowerShell as Administrator for device access

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/SarahGoel/ZeroTrace.git
cd ZeroTrace
```

2. **One-line setup and run (Windows PowerShell)**
```powershell
# Installs Python if missing, Node if missing, pip deps, builds web, and starts backend
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; \
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { winget install -e --id Python.Python.3 --accept-package-agreements --accept-source-agreements }; \
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements }; \
python -m pip install --upgrade pip; \
python -m pip install -r requirements.txt; \
pushd frontend/web; npm install; npm run build; popd; \
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

3. **One-line setup and run (macOS/Linux bash)**
```bash
# Requires sudo for package managers where needed
if ! command -v python3 >/dev/null 2>&1; then \
  if command -v brew >/dev/null 2>&1; then brew install python; \
  elif command -v apt >/dev/null 2>&1; then sudo apt update && sudo apt install -y python3 python3-pip; \
  elif command -v dnf >/dev/null 2>&1; then sudo dnf install -y python3 python3-pip; \
  elif command -v pacman >/dev/null 2>&1; then sudo pacman -S --noconfirm python python-pip; \
  fi; \
fi; \
if ! command -v node >/dev/null 2>&1; then \
  if command -v brew >/dev/null 2>&1; then brew install node; \
  elif command -v apt >/dev/null 2>&1; then curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt install -y nodejs; \
  elif command -v dnf >/dev/null 2>&1; then sudo dnf module enable -y nodejs:18 && sudo dnf install -y nodejs; \
  elif command -v pacman >/dev/null 2>&1; then sudo pacman -S --noconfirm nodejs npm; \
  fi; \
fi; \
python3 -m pip install --upgrade pip; \
python3 -m pip install -r requirements.txt; \
pushd frontend/web && npm install && npm run build && popd; \
python3 -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

4. **Access the application**
   - App (served by backend): http://127.0.0.1:8000
   - API Documentation: http://127.0.0.1:8000/docs

### 🎬 Demo Mode
For presentations, simply run backend + web or the Electron wrapper as below.

### Desktop App (PyQt)
```bash
python desktop/app.py
```

### Electron Wrapper (optional)
```bash
cd frontend/web
npm run electron
```

### Packaging
- Desktop (Windows):
  ```bash
  pip install pyinstaller
  pyinstaller --onefile --windowed desktop/app.py -n ZeroTraceDesktop
  ```
- Electron (production):
```bash
  cd frontend/web
  npm run build
  npm run electron:build
```

### Manual Setup

#### Backend Only
```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend Only
```bash
cd frontend/web
npm install
npm run dev
```

## ⚙️ Notes on Frontend Build

- The project uses Vite with an ESM config file: `frontend/web/vite.config.mjs`.
- If you see an error like "ESM file cannot be loaded by require" during build, ensure Node.js 18+ and run `npm install` before `npm run build` inside `frontend/web`.
- The presentation script `run_presentation.ps1` runs `npm install`, builds the frontend, verifies `dist/index.html`, then starts the backend which serves the built UI at `/`.

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: Python SQL toolkit and ORM
- **SQLite**: Lightweight database for development
- **Cryptography**: Cryptographic recipes and primitives
- **ReportLab**: PDF generation library
- **Uvicorn**: ASGI server for FastAPI

### Frontend
- **React 18**: Modern JavaScript library for building UIs
- **Vite**: Fast build tool and development server
- **React Icons**: Popular icon library
- **CSS3**: Modern styling with flexbox and grid

### Security
- **NIST 800-88**: Data sanitization standards
- **DoD 5220.22-M**: Department of Defense data sanitization
- **Cryptographic Erasure**: Key destruction for SSDs
- **Digital Signatures**: Tamper-proof report verification

## 📂 Repository Structure

```
ZeroTrace/
├── backend/                 # Python FastAPI backend
│   ├── __init__.py
│   ├── database.py         # Database operations and models
│   ├── main.py             # FastAPI application entry point
│   ├── models.py           # SQLAlchemy database models
│   ├── routes/             # API route definitions
│   │   ├── __init__.py
│   │   └── api.py          # Main API endpoints
│   ├── services/           # Core business logic
│   │   ├── secure_wipe.py  # Secure wipe service
│   │   ├── wipe_engine.py  # Wipe orchestration
│   │   └── wipe_methods.py # Wipe method implementations
│   └── utils/              # Utility functions
│       ├── certificate_generator.py  # Certificate generation
│       └── report.py       # Report utilities
├── frontend/               # React frontend
│   └── web/                # Vite React application
│       ├── node_modules/   # Node.js dependencies (auto-generated)
│       ├── package.json    # Node.js dependencies
│       ├── package-lock.json # Dependency lock file
│       ├── vite.config.js  # Vite configuration
│       └── src/            # React source code
│           ├── App.jsx     # Main application component
│           ├── App.css     # Main application styles
│           ├── index.css   # Base styles
│           ├── main.jsx    # Application entry point
│           └── components/ # React components
│               ├── CertificateViewer.jsx  # Certificate display
│               ├── DeviceList.jsx        # Device selection
│               ├── Reports.jsx           # Report management
│               ├── WipeOptions.jsx       # Method selection
│               └── WipeProgress.jsx      # Progress tracking
├── demo_script.py          # Demo presentation script
├── demo_setup.py           # Demo setup script
├── run.py                  # Unified application launcher
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
├── PRESENTATION_GUIDE.md   # Presentation guide
├── LICENSE                 # License file
└── .gitignore             # Git ignore rules
```

### 📁 Directory Descriptions

- **`backend/`**: Complete Python FastAPI backend with database models, API routes, and business logic
- **`frontend/web/`**: React application built with Vite for modern development experience
- **`backend/services/`**: Core wiping logic with support for multiple security standards
- **`backend/utils/`**: Utility functions for certificate generation and report creation
- **`backend/routes/`**: RESTful API endpoints for frontend communication
- **`frontend/web/src/components/`**: Modular React components for different UI sections

## 📜 Usage Guide

### 1. Device Selection
- Connect your storage device (USB, external drive, etc.)
- The application will automatically detect available devices
- Select the device(s) you want to wipe
- Review device information (type, size, model)

### 2. Method Selection
- **Recommended Methods**:
  - **Cryptographic Erase**: For SSDs (fastest, most secure)
  - **NIST 800-88**: For general use (industry standard)
  - **DoD 5220.22-M**: For high-security requirements
- **Advanced Methods**:
  - **Gutmann**: Maximum security (35 passes)
  - **ATA Sanitize**: Hardware-level erase
  - **NVMe Format**: For NVMe SSDs

### 3. Wipe Process
- Confirm your selection (data will be permanently destroyed)
- Monitor real-time progress
- View detailed status messages
- Wait for completion confirmation

### 4. Reports & Certificates
- Download PDF certificates of data destruction
- Verify digital signatures for authenticity
- Use reports for compliance and audit purposes

## 🔐 Security Considerations

### Data Destruction Methods

1. **Cryptographic Erasure** (Recommended for SSDs)
   - Destroys encryption keys
   - Makes data recovery impossible
   - Fastest method
   - Hardware-dependent

2. **NIST 800-88 Clear + Verify + Purge**
   - Industry standard process
   - Three-phase approach
   - Verifies successful erasure
   - Suitable for all device types

3. **DoD 5220.22-M**
   - Military-grade standard
   - Three-pass overwrite (0s, 1s, random)
   - Proven security track record
   - Slower but very secure

4. **Gutmann Method**
   - 35-pass overwrite
   - Maximum security
   - Very slow
   - For extreme security requirements

### Safety Features

- **Confirmation Required**: Multiple confirmation steps
- **Device Validation**: Prevents accidental system drive selection
- **Progress Monitoring**: Real-time status updates
- **Error Recovery**: Graceful handling of failures
- **Audit Logging**: Complete operation history

## 🚨 Important Warnings

⚠️ **CRITICAL**: This tool permanently destroys data. Recovery is impossible.

- **Backup Important Data**: Always backup before wiping
- **Verify Device Selection**: Double-check selected devices
- **System Drives**: Never wipe your system drive
- **External Drives Only**: Use only for external storage devices
- **Test First**: Use on non-critical data first

## 🔧 API Documentation

The backend provides a RESTful API with the following endpoints:

### Core Endpoints
- `GET /api/drives` - List available devices
- `POST /api/wipe` - Initiate wipe operation
- `GET /api/wipe/{session_id}/progress` - Get wipe progress
- `GET /api/wipe/sessions` - List wipe sessions
- `GET /api/wipe/methods` - Get available wipe methods

### Report Endpoints
- `GET /api/reports/{session_id}` - Download PDF report
- `GET /api/reports/{session_id}/signature` - Download signature

### Health Check
- `GET /api/health` - API health status

Full API documentation available at: http://localhost:8000/docs

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend/web
npm test
```

### Integration Tests
```bash
python run.py test
```

## 🐛 Troubleshooting

### Common Issues

1. **Permission Denied**
   - Run as administrator/root
   - Check device permissions
   - Ensure device is not mounted

2. **Device Not Detected**
   - Check device connection
   - Verify device is recognized by OS
   - Try refreshing device list

3. **Wipe Fails**
   - Check device health
   - Ensure sufficient permissions
   - Try different wipe method

4. **Frontend Not Loading**
   - Check if backend is running
   - Verify port 5173 is available
   - Check browser console for errors

### Logs and Debugging

- Backend logs: Check console output
- Frontend logs: Browser developer tools
- Database logs: `data/zerotrace.db`
- Report files: `reports/` directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

Licensed under the **GPL-3.0 License**.

This project is developed for the Smart India Hackathon 2025 (SIH25070) and is intended for educational and legitimate data destruction purposes only.

## ⚖️ Legal Disclaimer

This software is provided "as is" without warranty of any kind. Users are responsible for ensuring compliance with applicable laws and regulations. The developers are not liable for any data loss or misuse of this software.

## 📞 Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation

---

**Remember**: Always backup important data before using any data destruction tool!