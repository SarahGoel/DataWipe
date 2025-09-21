# 🔐 ZeroTrace – Secure Data Wiping Tool

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![React](https://img.shields.io/badge/React-18.2.0-blue)
![Vite](https://img.shields.io/badge/Vite-4.4.9-green)

A secure data wiping tool built for **trustworthy IT asset recycling**, ensuring irreversible deletion of sensitive information from storage devices. Developed for **Smart India Hackathon 2025** (SIH25070).

---

## 📂 Repository Structure

```
ZeroTrace/
├── backend/             # Python backend logic (APIs, services)
├── certificates/        # SSL/TLS certificates
├── frontend/            # React + Vite web interface
├── tests/               # Test cases
├── venv_new/            # Virtual environment (ignored in production)
├── generate_keys.py     # Script to generate cryptographic keys
├── run.py               # Entry point to run backend/frontend
├── index.html           # Landing page / static HTML
├── vite.config.js       # Frontend Vite config
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

---

## 🚀 Features

* **Multiple Wiping Methods**: DoD 5220.22-M, Gutmann, NIST 800-88, etc.
* **Cryptographic Erasure**: Secure key destruction for SSDs.
* **Frontend UI**: User-friendly React + Vite interface.
* **Backend API**: Python services for device detection, wiping, logging.
* **Reports & Logs**: Export compliance reports (CSV/PDF).
* **Cross-platform Support**: Works with HDDs, SSDs, USB drives.

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/SarahGoel/DataWipe.git
cd DataWipe
```

---

### 2️⃣ Backend Setup

```bash
cd backend
python -m venv venv
# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

pip install -r requirements.txt
python run.py
```

---

### 3️⃣ Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run at: [http://localhost:5173](http://localhost:5173)

---

## 🛠️ Tech Stack

* **Backend**: Python (FastAPI/Flask), SQLite/PostgreSQL
* **Frontend**: React + Vite, TailwindCSS
* **Security**: AES/RSA encryption, SSL/TLS
* **DevOps**: Docker, GitHub Actions

---

## 📜 Usage

1. Connect a storage device.
2. Choose a wiping method (single-pass, multi-pass, or cryptographic).
3. Start the wiping process and monitor progress in real-time.
4. Download the final **report** for compliance.

---

## 🔐 Security Considerations

* Implements **irreversible erasure** to prevent forensic recovery.
* Uses **cryptographic key destruction** for SSDs.
* Follows **NIST 800-88** and **DoD 5220.22-M** standards.

---

## 📄 License

Licensed under the **GPL-3.0 License**.
[View License](https://www.gnu.org/licenses/gpl-3.0)
