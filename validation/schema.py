"""
Validation Schema
Tracks what was verified, when, and from where
"""
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass
class VerificationRecord:
    """Record of a single data point verification"""
    field: str                    # e.g., "holdings", "burn_rate"
    value: any                    # The verified value
    source: str                   # Where it came from
    source_url: Optional[str]     # Direct link if available
    verified_at: str              # ISO timestamp
    verified_by: str              # "manual" or "automated"
    notes: Optional[str] = None   # Any discrepancies or context
    confidence: str = "high"      # "high", "medium", "low"


@dataclass
class CompanyValidation:
    """All validations for a single company"""
    ticker: str
    last_full_audit: str          # When all fields were checked
    records: dict                 # field -> VerificationRecord


def load_validation_log() -> dict:
    """Load existing validation records"""
    path = Path(__file__).parent / "validation_log.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_validation_log(data: dict):
    """Save validation records"""
    path = Path(__file__).parent / "validation_log.json"
    path.write_text(json.dumps(data, indent=2, default=str))


def log_verification(
    ticker: str,
    field: str,
    value: any,
    source: str,
    source_url: str = None,
    notes: str = None,
    confidence: str = "high",
    verified_by: str = "manual"
):
    """Log a verification of a data point"""
    log = load_validation_log()

    if ticker not in log:
        log[ticker] = {"records": {}}

    log[ticker]["records"][field] = {
        "value": value,
        "source": source,
        "source_url": source_url,
        "verified_at": datetime.now().isoformat(),
        "verified_by": verified_by,
        "notes": notes,
        "confidence": confidence,
    }

    save_validation_log(log)
    return log[ticker]["records"][field]


def get_stale_fields(ticker: str, max_age_days: int = 30) -> list:
    """Find fields that haven't been verified recently"""
    log = load_validation_log()
    stale = []

    if ticker not in log:
        return ["all"]  # Never verified

    now = datetime.now()
    for field, record in log[ticker].get("records", {}).items():
        verified_at = datetime.fromisoformat(record["verified_at"])
        age_days = (now - verified_at).days
        if age_days > max_age_days:
            stale.append((field, age_days))

    return stale


def generate_audit_report() -> str:
    """Generate a report of all validations and their freshness"""
    log = load_validation_log()
    lines = ["# Data Validation Audit Report", f"Generated: {datetime.now().isoformat()}", ""]

    for ticker, data in sorted(log.items()):
        lines.append(f"## {ticker}")
        for field, record in data.get("records", {}).items():
            age = (datetime.now() - datetime.fromisoformat(record["verified_at"])).days
            status = "✅" if age < 30 else "⚠️" if age < 90 else "❌"
            lines.append(f"  {status} **{field}**: {record['value']}")
            lines.append(f"     Source: {record['source']} ({age} days ago)")
            if record.get("notes"):
                lines.append(f"     Notes: {record['notes']}")
        lines.append("")

    return "\n".join(lines)
