import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[2] / "data" / "blockchain_ledger.json"

def _load():
    if not LEDGER.exists(): return []
    try: return json.loads(LEDGER.read_text(encoding="utf-8"))
    except Exception: return []

def anchor(sha256, issuer, certificate_id, fingerprint=None):
    chain = _load()
    body = {"sha256": sha256, "issuer": issuer, "certificate_id": certificate_id,
            "fingerprint": fingerprint, "timestamp": datetime.now(timezone.utc).isoformat(),
            "previous_hash": chain[-1]["block_hash"] if chain else "GENESIS"}
    block_hash = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    block = {"index": len(chain), **body, "block_hash": block_hash}
    chain.append(block); LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(chain, indent=2), encoding="utf-8")
    return {"anchored": True, "block_index": block["index"], "block_hash": block_hash, "previous_hash": body["previous_hash"], "ledger": "local-demo-chain"}

def verify_chain():
    chain = _load(); previous = "GENESIS"; problems=[]
    for i,b in enumerate(chain):
        body={k:b[k] for k in ("sha256","issuer","certificate_id","fingerprint","timestamp","previous_hash")}
        expected=hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        if b.get("index")!=i or b.get("previous_hash")!=previous or b.get("block_hash")!=expected:
            problems.append(i)
        previous=b.get("block_hash")
    return {"valid": not problems, "blocks": len(chain), "invalid_blocks": problems}

def find_by_hash(value):
    return [b for b in _load() if b.get("sha256")==value]
