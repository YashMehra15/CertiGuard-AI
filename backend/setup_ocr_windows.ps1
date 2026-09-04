Write-Host "CertiGuard AI OCR diagnostic"
if (Get-Command tesseract -ErrorAction SilentlyContinue) { tesseract --version; exit 0 }
$paths=@("C:\Program Files\Tesseract-OCR\tesseract.exe","C:\Program Files (x86)\Tesseract-OCR\tesseract.exe")
foreach($p in $paths){ if(Test-Path $p){Write-Host "Found: $p"; exit 0}}
Write-Host "Tesseract not found. Install Tesseract OCR and restart VS Code."
exit 1
