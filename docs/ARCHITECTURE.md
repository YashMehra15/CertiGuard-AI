# Architecture

```text
Certificate
   |
   +--> Native PDF text
   +--> Rendered pages / OCR
   +--> Embedded PDF images / QR
   +--> PDF hyperlink annotations
   |
   v
Evidence Fusion
   |
   +--> Issuer recognition
   +--> ID normalization
   +--> Name/course/date extraction
   +--> QR / Verifiable Credential claims
   +--> Official verification URL
   |
   v
Forensic Engine
   +--> QR ↔ PDF consistency
   +--> Registered identity consistency
   +--> Duplicate SHA-256
   +--> Same ID / different fingerprint
   +--> Metadata screening
   +--> Visual recompression screening
   |
   v
Explainable risk engine
   |
   +--> LIKELY AUTHENTIC
   +--> NEEDS MANUAL VERIFICATION
   +--> TAMPERING DETECTED
   |
   +--> local blockchain anchor
   +--> audit log
   +--> PDF report
```
