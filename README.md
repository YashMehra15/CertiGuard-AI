# CertiGuard AI 10.0 — Digital Certificate Forensics & Verification

A full-stack BCA major-project implementation for detecting altered academic/course certificates across heterogeneous issuers such as NPTEL, Saylor Academy, Analytics Vidhya, NIELIT, SWAYAM, Coursera, Great Learning and unknown providers.

## What this version adds

- Universal PDF/image extraction: native PDF text + OCR + PDF hyperlinks + embedded images.
- Issuer recognition using text, official verification domains and conservative template fingerprints.
- Issuer-aware certificate ID extraction. NPTEL prioritizes its long ID and QR; Saylor recognizes its certificate-code pattern; Analytics Vidhya handles date/ID layout.
- QR decoding from original embedded PDF images before page rendering.
- Verifiable Credential JSON parsing for QR payloads such as Wingspan/Infosys-style credentials.
- Cross-source consistency checks: name, course and certificate ID against QR claims.
- Optional registered-student/course consistency checks.
- Exact duplicate and same-certificate-ID/different-file detection.
- Basic PDF metadata and recompression forensic screening (screening only, not proof).
- Explainable tampering signals and confidence score.
- Local append-only-style blockchain demo ledger with chain verification.
- Student registration/login and admin role.
- Admin reference registry for authorized test records.
- Audit trail and dashboard analytics.
- Downloadable PDF authenticity report.
- Official verification source link when an issuer/QR exposes one.

## Demo credentials

Admin: `admin@certiguard.local` / `admin123`

## Run on Windows / VS Code

### Backend
```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: http://127.0.0.1:8000  | Swagger: http://127.0.0.1:8000/docs

### Frontend — second terminal
```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

### OCR
OCR is optional for certificates whose important fields exist in the PDF text/QR. For graphical issuer logos, install Tesseract and ensure it is at a standard path or set `TESSERACT_CMD`. Run:
```powershell
powershell -ExecutionPolicy Bypass -File backend\setup_ocr_windows.ps1
```

## Test strategy

Recommended supplied test set:
- NPTEL Java certificate
- NPTEL Soft Skills certificate
- Saylor C++ certificate
- Analytics Vidhya Generative AI with AWS certificate
- Infosys Springboard certificate
- NIELIT Yuva AI for All certificate

The system must not label missing QR/OCR/ID as fraud. A red result requires concrete conflict evidence such as PDF name vs QR name, certificate ID vs QR ID, registered identity mismatch, or same certificate ID appearing with materially conflicting fields.

## Architecture

Upload → Document analyzer → PDF text/OCR/QR/links → evidence fusion → issuer adapter → field extraction → official verification source → forensic consistency → duplicate/fingerprint analysis → risk engine → blockchain anchor → audit/report.

## Important limitation

Blockchain anchoring in this project is a local demonstrator ledger, not a public decentralized blockchain. Official issuer verification remains the authoritative source when available.
