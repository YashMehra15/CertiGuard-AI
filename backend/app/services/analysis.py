import hashlib, io, json, os, re
from pathlib import Path
from PIL import Image, ImageChops, ImageStat, ImageOps, ImageFilter

ISSUERS = {
    "Coursera": ["coursera"],
    "Saylor Academy": ["saylor academy", "saylor"],
    "NPTEL": ["nptel", "national programme on technology enhanced learning"],
    "NIELIT": ["nielit", "national institute of electronics and information technology", "skill india"],
    "SWAYAM": ["swayam"],
    "Great Learning": ["great learning", "greatlearning"],
    "Analytics Vidhya": ["analytics vidhya", "analyticsvidhya"],
    "Infosys Springboard": ["infosys springboard", "infosys", "wingspan", "onwingspan"],
}
OFFICIAL_DOMAINS={
    "NPTEL": ["nptel.ac.in"], "Saylor Academy":["saylor.org","learn.saylor.org"],
    "Analytics Vidhya":["analyticsvidhya.com"], "NIELIT":["nielit.gov.in","nielit.ac.in","skillindiadigital.gov.in"],
    "SWAYAM":["swayam.gov.in"], "Coursera":["coursera.org"], "Great Learning":["greatlearning.in","greatlearning.com"],
    "Infosys Springboard":["onwingspan.com","infosys.com"]
}

def sha256(data): return hashlib.sha256(data).hexdigest()
def normalize(v): return re.sub(r"[^a-z0-9]", "", str(v or "").lower())
def clean(v): return re.sub(r"\s+", " ", str(v or "")).strip(" \t\r\n.,;:()[]{}<>\"'")
def kind_of(data, filename):
    ext=Path(filename).suffix.lower()
    if data[:4]==b"%PDF" or ext==".pdf": return "PDF"
    if data[:8]==b"\x89PNG\r\n\x1a\n" or ext==".png": return "PNG"
    if data[:2]==b"\xff\xd8" or ext in (".jpg",".jpeg"): return "JPEG"
    return "UNKNOWN"

def pdf_text(data):
    try:
        from pypdf import PdfReader
        r=PdfReader(io.BytesIO(data)); text="\n".join(p.extract_text() or "" for p in r.pages).strip()
        meta={str(k):str(v) for k,v in (r.metadata or {}).items()}
        return text,{"pages":len(r.pages),"metadata":meta}
    except Exception as e: return "",{"error":str(e)}

def render_pages(data, limit=2):
    try:
        import fitz
        doc=fitz.open(stream=data,filetype="pdf"); pages=[]
        for i in range(min(limit,doc.page_count)):
            p=doc[i]; pix=p.get_pixmap(matrix=fitz.Matrix(2.2,2.2),alpha=False)
            pages.append(Image.frombytes("RGB",[pix.width,pix.height],pix.samples))
        doc.close(); return pages
    except Exception:return []

def pdf_links(data):
    links=[]
    try:
        import fitz
        doc=fitz.open(stream=data,filetype="pdf")
        for p in doc:
            for x in p.get_links():
                if x.get("uri"): links.append(x["uri"])
        doc.close()
    except Exception: pass
    return list(dict.fromkeys(links))

def embedded_images(data):
    out=[]
    try:
        import fitz
        doc=fitz.open(stream=data,filetype="pdf")
        for p in doc:
            for item in p.get_images(full=True):
                try:
                    pix=fitz.Pixmap(doc,item[0])
                    if pix.width<30 or pix.height<30: continue
                    mode="RGBA" if pix.n==4 else "RGB"
                    out.append(Image.frombytes(mode,[pix.width,pix.height],pix.samples).convert("RGB"))
                except Exception: pass
        doc.close()
    except Exception: pass
    return out

def tess_cmd():
    try:
        import pytesseract
        env=os.environ.get("TESSERACT_CMD")
        if env and Path(env).exists(): pytesseract.pytesseract.tesseract_cmd=env; return env
        for p in [r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe",r"C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe","/usr/bin/tesseract","/usr/local/bin/tesseract","/opt/homebrew/bin/tesseract"]:
            if Path(p).exists(): pytesseract.pytesseract.tesseract_cmd=p; return p
        return None
    except Exception:return None

def ocr(img):
    try:
        import pytesseract
        if not tess_cmd(): return "","TESSERACT_NOT_FOUND"
        scale=1.6 if max(img.size)<3500 else 1.15
        up=img.resize((int(img.width*scale),int(img.height*scale)),Image.Resampling.LANCZOS)
        g=ImageOps.autocontrast(ImageOps.grayscale(up)).filter(ImageFilter.SHARPEN)
        blocks=[]
        for psm in (6,11,12):
            t=pytesseract.image_to_string(g,config=f"--psm {psm}").strip()
            if t: blocks.append(t)
        lines=[]; seen=set()
        for b in blocks:
            for line in b.splitlines():
                line=clean(line)
                if line and normalize(line) not in seen: seen.add(normalize(line)); lines.append(line)
        return "\n".join(lines),None
    except Exception as e:return "",f"OCR_ERROR: {e}"

def extract_all_text(data, kind):
    if kind=="PDF":
        native,meta=pdf_text(data); pages=render_pages(data); ocr_parts=[]; errors=[]
        for p in pages[:2]:
            t,e=ocr(p)
            if t: ocr_parts.append(t)
            if e: errors.append(e)
        o="\n".join(ocr_parts)
        return native+"\n"+o if native and o else (native or o), {**meta,"pages_rendered":len(pages),"ocr_errors":errors[:5]}, ("PDF_TEXT+OCR" if native and o else "PDF_TEXT" if native else "PDF_OCR" if o else "UNAVAILABLE")
    try:
        im=Image.open(io.BytesIO(data)).convert("RGB"); t,e=ocr(im); return t,{"width":im.width,"height":im.height,"ocr_error":e},"IMAGE_OCR"
    except Exception as e:return "",{"error":str(e)},"UNAVAILABLE"

def detect_issuer(text,links):
    low=re.sub(r"\s+"," ",text.lower())
    # explicit text first
    for issuer,aliases in ISSUERS.items():
        if any(a in low for a in aliases): return issuer
    for u in links:
        l=u.lower()
        for issuer,domains in OFFICIAL_DOMAINS.items():
            if any(d in l for d in domains): return issuer
    # template fingerprints where branding can be image-only
    if re.search(r"saylor\s+academy\s+awards",low): return "Saylor Academy"
    if re.search(r"certificate\s+of\s+achievement",low) and re.search(r"\b[A-Z]{2,8}\d{2,4}:\s+",text): return "Saylor Academy"
    if re.search(r"awarded\s+to .*?successfully\s+completing",low): return "Analytics Vidhya"
    if re.search(r"verify\.onwingspan\.com|wingspan",low): return "Infosys Springboard"
    if re.search(r"programming\s+in\s+java|roll\s+no\.?|noc\s+certificate",low) and "nptel" in low: return "NPTEL"
    return "Unknown Issuer"

def extract_id(text,links,issuer,qr):
    if issuer=="NPTEL":
        candidates=re.findall(r"\bNPTEL\d{2}[A-Z]{2}\d{2,4}[A-Z]\d{5,}\b",text,re.I)
        for q in qr:
            candidates += re.findall(r"\bNPTEL\d{2}[A-Z]{2}\d{2,4}[A-Z]\d{5,}\b",q,re.I)
        if candidates:return max(candidates,key=len).upper()
    if issuer=="Saylor Academy":
        m=re.search(r"\b\d{10}[A-Z]{2}\b",text,re.I)
        if m:return m.group(0).upper()
        for u in links:
            m=re.search(r"[?&]code=([A-Za-z0-9]{6,})",u,re.I)
            if m:return m.group(1)
    if issuer=="Analytics Vidhya":
        m=re.search(r"\b\d{4}-\d{2}-\d{2}\s+([A-Za-z0-9_-]{6,40})\b",text)
        if m:return m.group(1)
    for u in links:
        for pat in (r"[?&](?:code|id|certificateId)=([A-Za-z0-9._/-]{6,})",r"/E_Certificate/([A-Za-z0-9_-]{8,})"):
            m=re.search(pat,u,re.I)
            if m:return m.group(1).upper()
    patterns=[r"(?im)^\s*(?:certificate|credential|verification|certification)\s*(?:id|no\.?|number|code)?\s*[:#-]\s*([A-Z0-9][A-Z0-9./_-]{5,})\s*$",r"(?im)^\s*roll\s*(?:no\.?|number)\s*[:#-]\s*([A-Z0-9][A-Z0-9./_-]{5,})\s*$"]
    bad={"JAN-APR","JUL-DEC","CERTIFICATE","COMPLETION","COURSE","PROGRAMMING"}
    for p in patterns:
        for m in re.finditer(p,text):
            c=clean(m.group(1)).upper()
            if c not in bad:return c
    return None

def extract_fields(text,issuer):
    n=re.sub(r"\s+"," ",text).strip(); lines=[clean(x) for x in text.splitlines() if clean(x)]
    out={"student_name":None,"course_line":None,"issue_date":None,"duration":None,"grade":None,"provider":issuer if issuer!="Unknown Issuer" else None}
    if issuer=="NPTEL":
        # course is usually before uppercase recipient; avoid session/score lines
        for i,l in enumerate(lines):
            if re.fullmatch(r"[A-Z][A-Z .'-]{2,70}",l) and len(l.split())>=2 and not re.search(r"NPTEL|ROLL|JAN|APR|JUL|DEC|COURSE|CREDITS|PROGRAMMING|CERTIFICATE|WEEK",l,re.I):
                out["student_name"]=l; idx=i; break
        else: idx=None
        if idx is not None:
            for j in range(idx-1,-1,-1):
                c=lines[j]
                if 2<=len(c.split())<=12 and not re.search(r"Jan-Apr|Jul-Dec|week course|credits|roll no|verify|recommended|certified|nptel",c,re.I): out["course_line"]=c; break
        m=re.search(r"\((\d+)\s*week\s+course\)",n,re.I)
        if m:out["duration"]=m.group(1)+" week course"
        return out
    if issuer=="Saylor Academy":
        # Prefer sentence-based extraction, then first two meaningful lines.
        m=re.search(r"Saylor\s+Academy\s+awards\s+(.+?)\s+this\s+certificate",n,re.I)
        if m:out["student_name"]=clean(m.group(1))
        m=re.search(r"certificate\s+of\s+achievement\s+for\s+(.+?)\s+Issue\s+Date",n,re.I)
        if m:out["course_line"]=clean(m.group(1))
        if not out["student_name"] and lines: out["student_name"]=clean(lines[0])
        if not out["course_line"] and len(lines)>1 and re.match(r"^[A-Z]{1,8}\d{2,4}:\s*",lines[1],re.I):out["course_line"]=lines[1]
        m=re.search(r"\b(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b",n,re.I)
        if m:out["issue_date"]=m.group(1)
        m=re.search(r"\b(\d+(?:\.\d+)?)\s*Hours\b",n,re.I)
        if m:out["duration"]=m.group(1)+" Hours"
        nums=re.findall(r"\b\d{1,3}\.\d{2}\b",n)
        if nums:out["grade"]=nums[-1]
        return out
    if issuer=="Analytics Vidhya":
        m=re.search(r"Awarded\s+to\s+(.+?)\s+For\s+successfully",n,re.I)
        if m:out["student_name"]=clean(m.group(1))
        m=re.search(r"For\s+successfully\s+completing\s+(?:the\s+)?(?:Free\s+)?Course\s+(.+?)(?=\s+Provided\s+by\b|\s+\d{4}-\d{2}-\d{2}\b|$)",n,re.I)
        if m:out["course_line"]=clean(m.group(1))
        m=re.search(r"\b(\d{4}-\d{2}-\d{2})\b",n)
        if m:out["issue_date"]=m.group(1)
        return out
    if issuer=="Infosys Springboard":
        for i,l in enumerate(lines):
            if re.match(r"the certificate is awarded to",l,re.I) and i>=2:
                out["student_name"]=lines[i-2]; out["course_line"]=lines[i-1]; break
        m=re.search(r"\b([A-Z][a-z]+\s+\d{1,2},\s+\d{4})\b",n)
        if m:out["issue_date"]=m.group(1)
        return out
    if issuer=="NIELIT":
        if "Yuva AI for All" in n:out["course_line"]="Yuva AI for All"
        dates=re.findall(r"\b\d{2}/\d{2}/\d{4}\b",n)
        if dates:out["issue_date"]=dates[-1]
        m=re.search(r"(\d+)\s+Hours?\s+(\d+)\s+Minutes?",n,re.I)
        if m:out["duration"]=f"{m.group(1)} Hours {m.group(2)} Minutes"
        # name after Mr./Ms./Mx.
        m=re.search(r"Mr\./Ms\./Mx\.\s+([A-Za-z][A-Za-z .'-]+?)(?=\s+in\s+the\s+job|\s+in\s+the\s+|\s+for\s+the\s+job)",n,re.I)
        if m:out["student_name"]=clean(m.group(1))
        return out
    # generic labelled extraction
    for i,l in enumerate(lines):
        m=re.match(r"(?:name|awarded to|presented to)\s*[:#-]\s*(.+)",l,re.I)
        if m and not out["student_name"]:out["student_name"]=clean(m.group(1))
        m=re.match(r"(?:course|course name|course title|program)\s*[:#-]\s*(.+)",l,re.I)
        if m and not out["course_line"]:out["course_line"]=clean(m.group(1))
    return out

def qr_decode_image(img):
    try:
        import cv2,numpy as np
        a=cv2.cvtColor(np.array(img),cv2.COLOR_RGB2BGR); det=cv2.QRCodeDetector(); vals=[]
        for c in [a]+[cv2.resize(a,None,fx=s,fy=s,interpolation=cv2.INTER_CUBIC) for s in (1.5,2,3)]:
            try:
                ok,decoded,_,_=det.detectAndDecodeMulti(c)
                if ok:
                    vals.extend([x for x in decoded if x])
            except Exception:pass
            try:
                v,_,_=det.detectAndDecode(c)
                if v:vals.append(v)
            except Exception:pass
        return vals
    except Exception:return []

def qr_values(data,kind):
    vals=[]
    if kind=="PDF":
        for im in embedded_images(data): vals.extend(qr_decode_image(im))
        if not vals:
            for p in render_pages(data): vals.extend(qr_decode_image(p))
    else:
        try:vals=qr_decode_image(Image.open(io.BytesIO(data)).convert("RGB"))
        except Exception:pass
    return list(dict.fromkeys(vals))

def qr_claims(qr):
    claims={}
    for q in qr:
        try:
            obj=json.loads(q)
            if isinstance(obj,dict):
                sub=obj.get("credentialSubject") or {}
                if isinstance(sub,dict):
                    for k,v in [("student_name",sub.get("issuedTo") or sub.get("name")),("course_line",sub.get("course") or sub.get("courseName")),("certificate_id",sub.get("certificateId") or sub.get("id"))]:
                        if v:claims[k]=str(v).rsplit("/",1)[-1]
        except Exception:pass
        m=re.search(r"NPTEL\d{2}[A-Z]{2}\d{2,4}[A-Z]\d{5,}",q,re.I)
        if m:claims["certificate_id"]=m.group(0).upper()
    return claims

def visual_forensics(data,kind):
    pages=render_pages(data) if kind=="PDF" else []
    if kind!="PDF":
        try:pages=[Image.open(io.BytesIO(data)).convert("RGB")]
        except Exception:pages=[]
    signals=[]
    if not pages:return {"available":False,"signals":[],"reason":"PDF/image rendering unavailable."}
    for im in pages:
        signals.append({"name":"Resolution","status":"PASS" if im.width>=800 and im.height>=500 else "UNKNOWN","detail":f"{im.width}×{im.height}"})
        try:
            b=io.BytesIO();im.save(b,format="JPEG",quality=90); rec=Image.open(io.BytesIO(b.getvalue())).convert("RGB")
            rms=sum(ImageStat.Stat(ImageChops.difference(im,rec)).rms)/3
            signals.append({"name":"Compression/noise consistency","status":"PASS" if rms<=12 else "UNKNOWN","detail":f"Recompression screening value {rms:.2f}"})
        except Exception:pass
    return {"available":True,"signals":signals,"reason":None}

def pdf_fingerprint(data):
    try:
        import fitz
        doc=fitz.open(stream=data,filetype="pdf"); chunks=[]
        for p in doc:
            chunks.append(p.get_text("text"))
        doc.close(); return hashlib.sha256("\n".join(chunks).encode()).hexdigest()
    except Exception:return None

def metadata_signals(data,kind):
    out=[]
    if kind=="PDF":
        _,m=pdf_text(data); meta=m.get("metadata",{})
        producer=(meta.get("/Producer") or meta.get("Producer") or "").lower(); creator=(meta.get("/Creator") or meta.get("Creator") or "").lower()
        if any(x in producer+" "+creator for x in ("photoshop","illustrator","gimp","canva")):
            out.append(("Editing software metadata","WARN",f"PDF metadata mentions {producer or creator}. This is a signal, not proof."))
        if meta.get("/ModDate") or meta.get("ModDate"):out.append(("PDF modification timestamp","INFO",str(meta.get("/ModDate") or meta.get("ModDate"))))
    return out

def analyze(data,filename,prior=None,submitted_name=None,submitted_course=None):
    kind=kind_of(data,filename); native,meta=pdf_text(data) if kind=="PDF" else ("",{})
    links=pdf_links(data) if kind=="PDF" else []
    text,technical,method=extract_all_text(data,kind)
    issuer=detect_issuer(text,links); qr=qr_values(data,kind); claims=qr_claims(qr)
    cid=extract_id(native or text,links,issuer,qr)
    fields=extract_fields(native or text,issuer)
    # OCR may contain visual-only values; only fill missing fields.
    ocr_fields=extract_fields(text,issuer)
    for k in fields:
        if not fields[k] and ocr_fields.get(k):fields[k]=ocr_fields[k]
    if claims.get("student_name") and issuer=="Infosys Springboard":fields["student_name"]=claims["student_name"]
    if claims.get("course_line") and issuer=="Infosys Springboard":fields["course_line"]=claims["course_line"]
    if not cid and claims.get("certificate_id"):cid=claims["certificate_id"]
    if issuer=="NPTEL" and claims.get("certificate_id"):cid=claims["certificate_id"] if not cid else max([cid,claims["certificate_id"]],key=len)
    evidence=[]; warnings=[]; tamper=[]
    def ev(name,status,detail,typ="AUTHENTICITY"):evidence.append({"name":name,"status":status,"detail":detail,"type":typ})
    if text:ev("Text extraction","PASS",f"{method}: readable certificate text extracted.")
    else:ev("Text extraction","UNKNOWN","No readable text extracted.","UNKNOWN")
    if issuer!="Unknown Issuer":ev("Issuer recognition","PASS",issuer)
    else:ev("Issuer recognition","UNKNOWN","Issuer not confidently recognized.","UNKNOWN");warnings.append("Issuer was not confidently recognized.")
    if cid:ev("Certificate ID","PASS",cid)
    else:ev("Certificate ID","UNKNOWN","No plausible certificate ID detected.","UNKNOWN");warnings.append("No certificate ID was confidently extracted.")
    if qr:
        ev("QR code","PASS",qr[0][:300]);
        domain_ok=False
        for d in OFFICIAL_DOMAINS.get(issuer,[]):
            if d in qr[0].lower():domain_ok=True
        if domain_ok:ev("QR issuer domain","PASS",f"QR payload references an official {issuer} domain.")
        elif qr[0].startswith(("http://","https://")):ev("QR issuer domain","WARN","QR URL does not match the recognized issuer domain.","FORENSICS");tamper.append("QR destination conflicts with issuer.")
    else:
        ev("QR code","UNKNOWN","No readable QR detected.","UNKNOWN")
        if issuer in ("Saylor Academy","Analytics Vidhya"):warnings.append("No QR detected; this issuer may use a web verification link or certificate ID instead.")
        else:warnings.append("No readable QR was detected; QR absence is not evidence of fraud.")
    for k,label in (("student_name","Student name"),("course_line","Course"),("issue_date","Issue date"),("duration","Duration"),("grade","Grade / score")):
        if fields.get(k):ev(label,"PASS",fields[k])
    # Cross-source consistency
    if claims.get("certificate_id") and cid:
        if normalize(claims["certificate_id"])==normalize(cid):ev("QR certificate ID consistency","PASS","Certificate ID matches QR claim.")
        else:ev("QR certificate ID consistency","WARN",f"QR ID {claims['certificate_id']} conflicts with certificate ID {cid}.","FORENSICS");tamper.append("Certificate ID conflicts with QR.")
    if claims.get("student_name") and fields.get("student_name"):
        if normalize(claims["student_name"])==normalize(fields["student_name"]):ev("QR identity consistency","PASS","QR identity matches extracted name.")
        else:ev("QR identity consistency","WARN",f"QR identity '{claims['student_name']}' conflicts with '{fields['student_name']}'.","FORENSICS");tamper.append("QR identity conflicts with certificate name.")
    if claims.get("course_line") and fields.get("course_line"):
        if normalize(claims["course_line"])==normalize(fields["course_line"]):ev("QR course consistency","PASS","QR course matches extracted course.")
        else:ev("QR course consistency","WARN",f"QR course '{claims['course_line']}' conflicts with '{fields['course_line']}'.","FORENSICS");tamper.append("QR course conflicts with certificate course.")
    # Registered account identity/course are intentionally NOT compared.
    # The uploader may verify certificates belonging to other people or courses.
    for n,s,d in metadata_signals(data,kind):ev(n,s,d,"FORENSICS" if s=="WARN" else "INFO")
    visual=visual_forensics(data,kind)
    if visual["available"]:
        for x in visual["signals"]:ev(x["name"],x["status"],x["detail"],"FORENSICS")
    else:warnings.append(visual["reason"])
    fp=pdf_fingerprint(data) if kind=="PDF" else hashlib.sha256(data).hexdigest()
    duplicate_exact=any(p.get("sha256")==sha256(data) for p in (prior or []))
    modified_same_id=[]
    if cid:
        modified_same_id=[p for p in (prior or []) if p.get("certificate_id") and normalize(p["certificate_id"])==normalize(cid) and p.get("sha256")!=sha256(data)]
    if duplicate_exact:ev("Exact duplicate fingerprint","INFO","This exact file was submitted previously.","INFO")
    if modified_same_id:
        ev("Same certificate ID / different file","WARN",f"{len(modified_same_id)} previous file(s) share this certificate ID but have a different SHA-256 fingerprint.","FORENSICS")
        tamper.append("Same certificate ID appears with a different file fingerprint.")
    # Identity/course changes against prior submissions with same certificate ID.
    for p in modified_same_id:
        try:
            old=json.loads(p.get("result") or "{}")
            of=old.get("fields",{})
            if fields.get("student_name") and of.get("student_name") and normalize(fields["student_name"])!=normalize(of["student_name"]):tamper.append("Same certificate ID has conflicting student names.")
            if fields.get("course_line") and of.get("course_line") and normalize(fields["course_line"])!=normalize(of["course_line"]):tamper.append("Same certificate ID has conflicting course names.")
        except Exception:pass
    tamper=list(dict.fromkeys(tamper));
    positive=sum(1 for x in evidence if x["type"]=="AUTHENTICITY" and x["status"]=="PASS")
    unknown=sum(1 for x in evidence if x["status"]=="UNKNOWN")
    authenticity=min(100,20+positive*8+ (15 if cid else 0)+(10 if issuer!="Unknown Issuer" else 0)+(10 if qr else 0))
    if not fields.get("student_name"):authenticity-=8
    if not fields.get("course_line"):authenticity-=6
    authenticity=max(0,min(100,authenticity))
    tamper_risk=min(100, len(tamper)*28)
    if tamper_risk>=60:verdict="TAMPERING DETECTED"
    elif authenticity>=70 and not tamper:verdict="LIKELY AUTHENTIC"
    else:verdict="NEEDS MANUAL VERIFICATION"
    official=None
    for u in links:
        if issuer!="Unknown Issuer" and any(d in u.lower() for d in OFFICIAL_DOMAINS.get(issuer,[])):official=u;break
    if not official and issuer=="NPTEL" and cid:official=f"https://nptel.ac.in/noc/E_Certificate/{cid}"
    if not official and issuer=="Saylor Academy" and cid:official=f"https://learn.saylor.org/admin/tool/certificate/index.php?code={cid}"
    return {"file_type":kind,"sha256":sha256(data),"issuer":issuer,"certificate_id":cid,"fields":fields,"extracted_text":text[:15000],"qr_values":qr,"qr_claims":claims,"official_verification_url":official,"technical":{**technical,"embedded_links":links[:30],"text_fingerprint":fp},"evidence":evidence,"warnings":list(dict.fromkeys(warnings)),"authenticity_confidence":authenticity,"tampering_risk":tamper_risk,"verdict":verdict,"concrete_tamper_signals":tamper,"duplicate_exact":duplicate_exact,"modified_same_certificate_id":bool(modified_same_id),"disclaimer":"Automated risk assessment. A definitive authenticity decision requires verification against the issuer's authoritative record."}
