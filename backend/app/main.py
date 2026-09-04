
import json
import sqlite3
import uuid
import hashlib
import hmac
import base64
import time

from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from .services.analysis import analyze
from .services.blockchain import anchor, verify_chain, find_by_hash
from .services.report import make_report


# ============================================================
# CONFIGURATION
# ============================================================

BASE = Path(__file__).resolve().parents[1]
DB = BASE / "certiguard.db"
SECRET = b"certiguard-local-demo-secret-change-me"

app = FastAPI(
    title="CertiGuard AI",
    version="11.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================
# DATABASE
# ============================================================

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c


def init():
    c = db()

    c.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE,
            password_hash TEXT,
            role TEXT,
            course TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS verifications (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            filename TEXT,
            sha256 TEXT,
            issuer TEXT,
            certificate_id TEXT,
            verdict TEXT,
            authenticity REAL,
            tamper_risk REAL,
            result TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT,
            verification_id TEXT,
            detail TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS issuer_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            issuer TEXT,
            certificate_id TEXT,
            student_name TEXT,
            course TEXT,
            issue_date TEXT,
            source_url TEXT,
            created_at TEXT
        );
        """
    )

    c.commit()

    # Create default administrator account.
    if not c.execute(
        "SELECT 1 FROM users WHERE email=?",
        ("admin@certiguard.local",)
    ).fetchone():

        c.execute(
            """
            INSERT INTO users
            (id, name, email, password_hash, role, course, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                "Administrator",
                "admin@certiguard.local",
                hashlib.sha256(
                    b"admin123"
                ).hexdigest(),
                "admin",
                "",
                datetime.now(timezone.utc).isoformat()
            )
        )

    c.commit()
    c.close()


init()


# ============================================================
# AUTHENTICATION
# ============================================================

def token(uid, role):
    payload = base64.urlsafe_b64encode(
        json.dumps(
            {
                "uid": uid,
                "role": role,
                "exp": time.time() + 86400
            }
        ).encode()
    ).decode().rstrip("=")

    signature = hmac.new(
        SECRET,
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    return payload + "." + signature


def auth(authorization):
    if not authorization:
        return None

    try:
        scheme, token_value = authorization.split(" ", 1)

        if scheme.lower() != "bearer":
            return None

        payload, signature = token_value.split(".", 1)

        expected_signature = hmac.new(
            SECRET,
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(
            signature,
            expected_signature
        ):
            return None

        decoded = base64.urlsafe_b64decode(
            payload + "=" * ((4 - len(payload) % 4) % 4)
        )

        data = json.loads(decoded)

        if data["exp"] < time.time():
            return None

        return data

    except Exception:
        return None


# ============================================================
# PYDANTIC MODELS
# ============================================================

class Login(BaseModel):
    email: str
    password: str


class Register(BaseModel):
    name: str
    email: str
    password: str
    course: str = ""


class Registry(BaseModel):
    issuer: str
    certificate_id: str
    student_name: str
    course: str
    issue_date: str = ""
    source_url: str = ""


class VerifyOptions(BaseModel):
    student_name: str = ""
    course: str = ""


# ============================================================
# BASIC ROUTES
# ============================================================

@app.get("/")
def root():
    return {
        "service": "CertiGuard AI",
        "version": "11.0",
        "features": [
            "account-independent verification",
            "universal extraction",
            "QR/VC analysis",
            "tampering forensics",
            "duplicate detection",
            "blockchain",
            "reports",
            "RBAC",
            "audit logs"
        ]
    }


@app.get("/api/health")
def health():

    tesseract_windows = Path(
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    tesseract_linux = Path(
        "/usr/bin/tesseract"
    )

    return {
        "status": "ok",
        "version": "11.0",
        "ocr_available": (
            tesseract_windows.exists()
            or tesseract_linux.exists()
        )
    }


# ============================================================
# AUTH - LOGIN
# ============================================================

@app.post("/api/auth/login")
def login(x: Login):

    c = db()

    user = c.execute(
        "SELECT * FROM users WHERE email=?",
        (x.email.lower(),)
    ).fetchone()

    c.close()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_hash = hashlib.sha256(
        x.password.encode()
    ).hexdigest()

    if password_hash != user["password_hash"]:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return {
        "token": token(
            user["id"],
            user["role"]
        ),
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "course": user["course"]
        }
    }


# ============================================================
# AUTH - REGISTER
# ============================================================

@app.post("/api/auth/register")
def register(x: Register):

    c = db()
    uid = str(uuid.uuid4())

    try:

        c.execute(
            """
            INSERT INTO users
            (id, name, email, password_hash, role, course, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                uid,
                x.name,
                x.email.lower(),
                hashlib.sha256(
                    x.password.encode()
                ).hexdigest(),
                "student",
                x.course,
                datetime.now(timezone.utc).isoformat()
            )
        )

        c.commit()

    except sqlite3.IntegrityError:

        c.close()

        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    c.close()

    return {
        "message": "Registration successful",
        "user_id": uid
    }


# ============================================================
# CURRENT USER
# ============================================================

@app.get("/api/me")
def me(
    authorization: str = Header(default="")
):

    data = auth(authorization)

    if not data:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    c = db()

    user = c.execute(
        """
        SELECT id, name, email, role, course, created_at
        FROM users
        WHERE id=?
        """,
        (data["uid"],)
    ).fetchone()

    c.close()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return dict(user)


# ============================================================
# CERTIFICATE VERIFICATION
# ============================================================

@app.post("/api/verify")
async def verify(
    file: UploadFile = File(...),
    authorization: str = Header(default=""),
    student_name: str = "",
    course: str = ""
):

    data = await file.read()

    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Maximum file size is 20 MB"
        )

    account = auth(authorization)

    c = db()

    prior = [
        dict(row)
        for row in c.execute(
            """
            SELECT
                id,
                filename,
                sha256,
                issuer,
                certificate_id,
                result
            FROM verifications
            """
        ).fetchall()
    ]

    # IMPORTANT:
    # The logged-in user's name/course is NOT used as an
    # authenticity requirement.
    #
    # This allows verification of certificates belonging to
    # any student and any course/provider.

    result = analyze(
        data,
        file.filename,
        prior
    )

    verification_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    result["verification_id"] = verification_id

    result["blockchain"] = anchor(
        result["sha256"],
        result["issuer"],
        result["certificate_id"],
        result["technical"].get("text_fingerprint")
    )

    c.execute(
        """
        INSERT INTO verifications
        (
            id,
            user_id,
            filename,
            sha256,
            issuer,
            certificate_id,
            verdict,
            authenticity,
            tamper_risk,
            result,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            verification_id,
            account["uid"] if account else None,
            file.filename,
            result["sha256"],
            result["issuer"],
            result["certificate_id"],
            result["verdict"],
            result["authenticity_confidence"],
            result["tampering_risk"],
            json.dumps(result),
            now
        )
    )

    c.execute(
        """
        INSERT INTO audit_logs
        (
            user_id,
            action,
            verification_id,
            detail,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            account["uid"] if account else None,
            "CERTIFICATE_ANALYSIS",
            verification_id,
            result["verdict"],
            now
        )
    )

    c.commit()
    c.close()

    return result


# ============================================================
# VERIFICATION HISTORY
# ============================================================

@app.get("/api/verifications")
def verifications(
    authorization: str = Header(default="")
):

    account = auth(authorization)
    c = db()

    if account and account["role"] != "admin":

        rows = c.execute(
            """
            SELECT
                id,
                filename,
                sha256,
                issuer,
                certificate_id,
                verdict,
                authenticity,
                tamper_risk,
                created_at
            FROM verifications
            WHERE user_id=?
            ORDER BY created_at DESC
            """,
            (account["uid"],)
        ).fetchall()

    else:

        rows = c.execute(
            """
            SELECT
                id,
                filename,
                sha256,
                issuer,
                certificate_id,
                verdict,
                authenticity,
                tamper_risk,
                created_at
            FROM verifications
            ORDER BY created_at DESC
            """
        ).fetchall()

    c.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# SINGLE VERIFICATION
# ============================================================

@app.get("/api/verifications/{vid}")
def verification(vid: str):

    c = db()

    row = c.execute(
        "SELECT result FROM verifications WHERE id=?",
        (vid,)
    ).fetchone()

    c.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Verification not found"
        )

    return json.loads(row["result"])


# ============================================================
# PDF REPORT
# ============================================================

@app.get("/api/reports/{vid}.pdf")
def report(vid: str):

    c = db()

    row = c.execute(
        "SELECT result FROM verifications WHERE id=?",
        (vid,)
    ).fetchone()

    c.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Verification not found"
        )

    pdf = make_report(
        json.loads(row["result"])
    )

    return Response(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f"attachment; filename=CertiGuard_{vid[:8]}.pdf"
        }
    )


# ============================================================
# AUDIT LOGS
# ============================================================

@app.get("/api/audit-logs")
def logs():

    c = db()

    rows = c.execute(
        """
        SELECT *
        FROM audit_logs
        ORDER BY created_at DESC
        LIMIT 500
        """
    ).fetchall()

    c.close()

    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# STATISTICS
# ============================================================

@app.get("/api/stats")
def stats():

    c = db()

    rows = c.execute(
        """
        SELECT verdict, COUNT(*) n
        FROM verifications
        GROUP BY verdict
        """
    ).fetchall()

    issuers = c.execute(
        """
        SELECT issuer, COUNT(*) n
        FROM verifications
        GROUP BY issuer
        ORDER BY n DESC
        """
    ).fetchall()

    recent = c.execute(
        """
        SELECT
            filename,
            issuer,
            authenticity,
            tamper_risk,
            verdict,
            created_at
        FROM verifications
        ORDER BY created_at DESC
        LIMIT 12
        """
    ).fetchall()

    c.close()

    return {
        "total": sum(row["n"] for row in rows),

        "counts": {
            row["verdict"]: row["n"]
            for row in rows
        },

        "issuers": [
            dict(row)
            for row in issuers
        ],

        "recent": [
            dict(row)
            for row in recent
        ]
    }


# ============================================================
# BLOCKCHAIN
# ============================================================

@app.get("/api/blockchain/verify")
def chain():

    return verify_chain()


@app.get("/api/blockchain/search")
def chain_search(sha256: str):

    return find_by_hash(sha256)


# ============================================================
# ADMIN REGISTRY
# ============================================================

@app.post("/api/admin/registry")
def registry(
    x: Registry,
    authorization: str = Header(default="")
):

    account = auth(authorization)

    if not account or account["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    c = db()

    c.execute(
        """
        INSERT INTO issuer_registry
        (
            issuer,
            certificate_id,
            student_name,
            course,
            issue_date,
            source_url,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            x.issuer,
            x.certificate_id,
            x.student_name,
            x.course,
            x.issue_date,
            x.source_url,
            datetime.now(timezone.utc).isoformat()
        )
    )

    c.commit()
    c.close()

    return {
        "message": "Registry record added"
    }


# ============================================================
# ADMIN REGISTRY LIST
# ============================================================

@app.get("/api/admin/registry")
def registry_list(
    authorization: str = Header(default="")
):

    account = auth(authorization)

    if not account or account["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    c = db()

    rows = c.execute(
        """
        SELECT *
        FROM issuer_registry
        ORDER BY id DESC
        """
    ).fetchall()

    c.close()

    return [
        dict(row)
        for row in rows
    ]
