# CertiGuard AI
A full-stack certificate forensics and verification platform that detects tampered or fraudulent academic/course certificates across multiple issuers, backed by a local blockchain-style audit ledger.

---

## 🚀 Features
* Universal PDF/image extraction (native PDF text + OCR + hyperlinks + embedded images)
* Multi-issuer recognition (NPTEL, Saylor Academy, Analytics Vidhya, NIELIT, SWAYAM, Coursera, Great Learning, and unknown providers)
* Issuer-aware certificate ID extraction and QR code decoding
* Verifiable Credential (VC) JSON parsing for QR payloads
* Cross-source consistency checks (name, course, certificate ID vs QR claims)
* Duplicate and same-ID/different-file tampering detection
* PDF metadata and recompression forensic screening
* Explainable tampering signals with confidence scoring
* Local append-only blockchain demo ledger with chain verification
* Role-based authentication (Student / Admin)
* Admin reference registry, audit trail, and dashboard analytics
* Downloadable PDF authenticity report

---

## 🛠 Tech Stack

### Frontend:
* React.js
* Vite
* JavaScript (JSX)
* lucide-react

### Backend:
* Python
* FastAPI
* SQLite
* PyMuPDF / pypdf (PDF parsing)
* OpenCV + Pillow (image processing)
* pytesseract (OCR)
* ReportLab (PDF report generation)

---

## ⚙️ How to Run Locally

Clone the repository:
```bash
git clone https://github.com/YashMehra15/CertiGuard.git
```

Navigate to project folder:
```bash
cd CertiGuard
```

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Create `.env` file in `backend/` (see `.env.example`):
```env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

Backend API → http://127.0.0.1:8000
Swagger Docs → http://127.0.0.1:8000/docs

### Frontend — second terminal
```bash
cd frontend
npm install
npm run dev
```

Frontend → http://localhost:5173

### OCR (optional)
OCR is only needed for certificates whose fields aren't present in PDF text/QR. Install Tesseract and set `TESSERACT_CMD`, or run:
```powershell
powershell -ExecutionPolicy Bypass -File backend\setup_ocr_windows.ps1
```

---

## 🌐 Local Development URLs
* Frontend → http://localhost:5173
* Backend → http://127.0.0.1:8000

---

## 🔑 Demo Credentials
Admin: `admin@certiguard.local` / `admin123`

---

## 🎯 Purpose
This project demonstrates a complete certificate verification system with issuer-aware forensic analysis, QR/VC validation, tampering detection, and a local blockchain-anchored audit trail.

> **Note:** Blockchain anchoring here is a local demonstrator ledger, not a public decentralized blockchain. Official issuer verification remains the authoritative source when available.

---

## 👨‍💻 Developed by
Yash Mehra

## ⭐ Support
If you like this project, give it a ⭐ on GitHub and share it!
