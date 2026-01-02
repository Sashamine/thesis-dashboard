r"""
Data Validation Monitor
Scheduled script to check data freshness and run validations

Usage:
    python -m validation.monitor              # Check staleness only
    python -m validation.monitor --validate   # Check and validate stale items
    python -m validation.monitor --report     # Generate audit report

Schedule via Windows Task Scheduler:
    Action: Start a program
    Program: python
    Arguments: -m validation.monitor --validate
    Start in: C:\Users\edwin\thesis_dashboard
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from validation.schema import (
    load_validation_log,
    save_validation_log,
    get_stale_fields,
    generate_audit_report,
    log_verification,
)
from validation.sources import VALIDATION_RULES, COMPANY_SOURCES, DATA_SOURCES
from config import (
    DAT_COMPANIES,
    BTC_DAT_COMPANIES,
    SOL_DAT_COMPANIES,
    HYPE_DAT_COMPANIES,
    BNB_DAT_COMPANIES,
)


# All companies to monitor
ALL_COMPANIES = {
    "ETH": DAT_COMPANIES,
    "BTC": BTC_DAT_COMPANIES,
    "SOL": SOL_DAT_COMPANIES,
    "HYPE": HYPE_DAT_COMPANIES,
    "BNB": BNB_DAT_COMPANIES,
}

# Fields to check per company type (field names match config.py)
MONITORED_FIELDS = {
    "ETH": ["eth_holdings", "staking_pct", "quarterly_burn_usd"],
    "BTC": ["holdings", "quarterly_burn_usd"],  # BTC uses 'holdings' field
    "SOL": ["holdings", "staking_pct", "quarterly_burn_usd"],  # SOL uses 'holdings' field
    "HYPE": ["holdings", "quarterly_burn_usd"],  # HYPE treasury companies
    "BNB": ["holdings", "quarterly_burn_usd"],  # BNB treasury companies
}


def get_data_health_summary() -> Dict:
    """
    Get overall data health summary for dashboard display
    Returns dict with health status per company and overall metrics
    """
    log = load_validation_log()
    now = datetime.now()

    summary = {
        "generated_at": now.isoformat(),
        "overall": {
            "total_companies": 0,
            "verified_companies": 0,
            "stale_companies": 0,
            "never_verified": 0,
        },
        "companies": {},
        "stale_items": [],
    }

    # Check each company type
    for asset_type, companies in ALL_COMPANIES.items():
        fields = MONITORED_FIELDS.get(asset_type, [])

        for ticker, company in companies.items():
            summary["overall"]["total_companies"] += 1

            company_status = {
                "name": company.get("name", ticker),
                "asset_type": asset_type,
                "fields": {},
                "overall_status": "unknown",
                "last_verified": None,
            }

            if ticker not in log:
                summary["overall"]["never_verified"] += 1
                company_status["overall_status"] = "never_verified"
                for field in fields:
                    company_status["fields"][field] = {
                        "status": "never_verified",
                        "age_days": None,
                    }
                    summary["stale_items"].append({
                        "ticker": ticker,
                        "field": field,
                        "reason": "Never verified",
                    })
            else:
                records = log[ticker].get("records", {})
                all_fresh = True
                any_verified = False
                latest_verification = None

                for field in fields:
                    if field not in records:
                        company_status["fields"][field] = {
                            "status": "never_verified",
                            "age_days": None,
                        }
                        all_fresh = False
                        summary["stale_items"].append({
                            "ticker": ticker,
                            "field": field,
                            "reason": "Never verified",
                        })
                    else:
                        record = records[field]
                        verified_at = datetime.fromisoformat(record["verified_at"])
                        age_days = (now - verified_at).days
                        any_verified = True

                        # Track latest verification
                        if latest_verification is None or verified_at > latest_verification:
                            latest_verification = verified_at

                        # Get max age for this field type
                        max_age = 30  # default
                        for rule_key, rule in VALIDATION_RULES.items():
                            if rule_key in field:
                                max_age = rule.get("max_age_days", 30)
                                break

                        if age_days > max_age:
                            status = "stale"
                            all_fresh = False
                            summary["stale_items"].append({
                                "ticker": ticker,
                                "field": field,
                                "reason": f"{age_days} days old (max: {max_age})",
                            })
                        elif age_days > max_age * 0.7:
                            status = "warning"
                        else:
                            status = "fresh"

                        company_status["fields"][field] = {
                            "status": status,
                            "age_days": age_days,
                            "value": record.get("value"),
                            "source": record.get("source"),
                        }

                if all_fresh and any_verified:
                    company_status["overall_status"] = "healthy"
                    summary["overall"]["verified_companies"] += 1
                elif any_verified:
                    company_status["overall_status"] = "stale"
                    summary["overall"]["stale_companies"] += 1

                if latest_verification:
                    company_status["last_verified"] = latest_verification.isoformat()

            summary["companies"][ticker] = company_status

    return summary


def check_staleness() -> List[Tuple[str, str, int]]:
    """
    Check all companies for stale data
    Returns list of (ticker, field, age_days) tuples
    """
    stale_items = []

    for asset_type, companies in ALL_COMPANIES.items():
        for ticker in companies.keys():
            stale = get_stale_fields(ticker)
            if stale == ["all"]:
                stale_items.append((ticker, "all", -1))
            else:
                for field, age in stale:
                    stale_items.append((ticker, field, age))

    return stale_items


def run_monitor(validate: bool = False, report: bool = False) -> None:
    """Main monitor function"""
    print(f"Data Validation Monitor - {datetime.now().isoformat()}")
    print("=" * 60)

    # Get health summary
    summary = get_data_health_summary()

    # Print overall stats
    overall = summary["overall"]
    print(f"\nOverall Status:")
    print(f"  Total companies: {overall['total_companies']}")
    print(f"  Verified & fresh: {overall['verified_companies']}")
    print(f"  Stale data: {overall['stale_companies']}")
    print(f"  Never verified: {overall['never_verified']}")

    # Print stale items
    if summary["stale_items"]:
        print(f"\nStale Items ({len(summary['stale_items'])}):")
        for item in summary["stale_items"]:
            print(f"  - {item['ticker']}.{item['field']}: {item['reason']}")
    else:
        print("\nAll data is fresh!")

    # Generate report if requested
    if report:
        report_text = generate_audit_report()
        report_path = Path(__file__).parent / "audit_report.md"
        report_path.write_text(report_text)
        print(f"\nAudit report saved to: {report_path}")

    # Save health summary for dashboard
    summary_path = Path(__file__).parent / "health_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nHealth summary saved to: {summary_path}")

    if validate and summary["stale_items"]:
        print("\n" + "=" * 60)
        print("VALIDATION MODE")
        print("Note: Automated validation requires API integrations.")
        print("Currently logging items that need manual verification.")
        print("=" * 60)

        # For now, just flag items needing attention
        # Full automation would integrate with data-validator agent
        for item in summary["stale_items"]:
            print(f"\nNeeds verification: {item['ticker']} - {item['field']}")
            source_info = COMPANY_SOURCES.get(item['ticker'], {})
            if source_info:
                print(f"  Sources: {source_info}")


def main():
    parser = argparse.ArgumentParser(description="Data Validation Monitor")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run validation on stale items",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate full audit report",
    )

    args = parser.parse_args()
    run_monitor(validate=args.validate, report=args.report)


if __name__ == "__main__":
    main()
