# CertiGuard AI

An advanced certificate verification and tampering detection platform that analyzes digital certificates using multiple layers of evidence including PDF forensics, OCR, QR verification, issuer validation, cryptographic fingerprinting, and explainable risk analysis.

---

## 🚀 Features

* Certificate Upload & Verification
* Multi-Issuer Certificate Support
* PDF Text & Document Forensics
* OCR-based Certificate Analysis
* QR Code Detection & Verification
* PDF Hyperlink Verification
* Issuer-specific Validation Rules
* Certificate ID Extraction
* SHA-256 Certificate Fingerprinting
* Duplicate Certificate Detection
* Same Certificate ID / Different Fingerprint Detection
* Metadata & Visual Screening
* Explainable Risk & Confidence Analysis
* Fraud / Tampering Signal Detection
* Local Blockchain-style Audit Ledger
* Complete Verification Audit Logs
* Downloadable PDF Verification Reports
* REST API for Certificate Verification
* Modern React Dashboard
* SQLite-based Local Database
* Account-independent Certificate Verification

---

## 🏢 Supported Issuers

CertiGuard AI is designed to support certificates from multiple educational and professional platforms, including:

* NPTEL
* SWAYAM
* Saylor Academy
* NIELIT
* Analytics Vidhya
* Infosys Springboard
* Coursera
* Great Learning
* Other supported certificate formats

---

## 🧠 Verification & Detection System

CertiGuard AI does not rely on a single verification method. It combines multiple evidence layers:

```
Certificate PDF
      │
      ├── Native PDF Text
      ├── OCR Analysis
      ├── Embedded Images
      ├── QR Code Detection
      ├── QR Destination Analysis
      ├── PDF Hyperlinks
      ├── Issuer Validation
      ├── Certificate ID Extraction
      ├── SHA-256 Fingerprint
      ├── Metadata Analysis
      └── Visual Screening
              │
              ▼
       Evidence Aggregation
              │
              ▼
      Explainable Risk Engine
              │
              ▼
     Verification Result
```

Missing evidence — such as an unavailable QR code or OCR result — is treated as **UNKNOWN**, rather than automatically being considered fraudulent.

Concrete conflicts between independent evidence sources can increase the tampering risk.

---

## 🛠 Tech Stack

### Frontend:
* React.js
* Vite
* JavaScript
* CSS
* Lucide React

### Backend:
* Python
* FastAPI
* Uvicorn
* PyMuPDF
* OpenCV
* OCR
* QR Code Processing

### Database:
* SQLite

### Security & Verification:
* SHA-256 Cryptographic Hashing
* PDF Forensics
* QR Verification
* Issuer-specific Rules
* Evidence-based Risk Analysis
* Blockchain-style Audit Ledger

### Reporting:
* PDF Report Generation

---

## 📁 Project Structure

```
CertiGuard-AI/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   └── services/
│   │       ├── analysis.py
│   │       ├── blockchain.py
│   │       └── report.py
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── setup_ocr_windows.ps1
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx
│   │   └── style.css
│   │
│   ├── index.html
│   ├── package.json
│   └── package-lock.json
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── DEMO_FLOW.md
│
├── tests/
│   └── test_analysis.py
│
├── .gitignore
└── README.md
```

---

## ⚙️ How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/YashMehra15/CertiGuard-AI.git
```

Navigate to the project:

```bash
cd CertiGuard-AI
```

### 2. Setup Backend

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows:

```bash
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file inside the `backend` directory. Use `.env.example` as a reference:

```env
APP_ENV=development
SECRET_KEY=your_secret_key
```

### 4. Setup OCR

For Windows, run:

```powershell
.\setup_ocr_windows.ps1
```

Make sure the required OCR components are available in your system `PATH`.

### 5. Start Backend

From the backend directory:

```bash
uvicorn app.main:app --reload
```

Backend will run at:

```
http://localhost:8000
```

FastAPI Swagger documentation:

```
http://localhost:8000/docs
```

### 6. Setup Frontend

Open another terminal and navigate to:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Frontend will run at:

```
http://localhost:5173
```

---

## 🌐 Local Development URLs

* Frontend → http://localhost:5173
* Backend API → http://localhost:8000
* API Documentation → http://localhost:8000/docs

---

## 🔍 Verification Workflow

A typical certificate verification process:

```
Upload Certificate
        ↓
Extract PDF Evidence
        ↓
Analyze Native Text
        ↓
Perform OCR
        ↓
Detect QR Code
        ↓
Analyze QR Destination
        ↓
Extract Certificate Metadata
        ↓
Identify Issuer
        ↓
Generate Certificate Fingerprint
        ↓
Check Duplicate / Conflict Evidence
        ↓
Calculate Explainable Risk
        ↓
Generate Verification Result
        ↓
Store Audit Record
        ↓
Generate PDF Report
```

---

## 📊 Verification Results

CertiGuard AI provides an evidence-based verification result rather than relying only on a simple valid/invalid classification.

Possible outcomes include:

* Verified
* Likely Authentic
* Needs Manual Verification
* Potentially Tampered
* Insufficient Evidence

The system also provides:

* Confidence score
* Tampering risk
* Evidence collected
* Verification signals
* Fraud/tampering indicators
* Issuer information
* Certificate information
* Audit information

---

## 🔐 Security

CertiGuard AI uses cryptographic and forensic techniques to strengthen certificate verification.

### SHA-256 Fingerprinting

Every analyzed certificate can be represented using a cryptographic SHA-256 fingerprint. This allows the system to detect:

* Duplicate certificates
* Previously analyzed documents
* Same certificate ID with different document fingerprints
* Potential document modifications

---

## ⛓️ Audit Ledger

CertiGuard AI maintains a local blockchain-style audit ledger for verification events. Each audit entry can contain:

* Certificate fingerprint
* Verification result
* Timestamp
* Previous ledger hash
* Current ledger hash

This creates a tamper-evident chain of verification records.

---

## 🧪 Testing

Run the analysis tests from the project root:

```bash
pytest
```

The test suite validates important certificate analysis and risk-detection functionality.

---

## 🎯 Purpose

CertiGuard AI is designed as a major academic project demonstrating the practical application of:

* Artificial Intelligence
* Digital Forensics
* Cybersecurity
* Document Analysis
* Cryptographic Hashing
* QR Verification
* OCR
* REST APIs
* Full-stack Web Development
* Database Management
* Explainable Risk Analysis

The project demonstrates how multiple independent evidence sources can be combined to make certificate verification more reliable and explainable.

---

## 👨‍💻 Developed By

**Yash Mehra**
BCA Student, Graphic Era Hill University

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub and share it!
