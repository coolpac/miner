"""US/UK Business Entity Lookup — main CLI.

Usage:
    python main.py search "Tesla" --source opencorporates
    python main.py search "Apple" --source sec
    python main.py search "Tesco" --source uk
    python main.py search "Google" --jurisdiction us_ca
    python main.py filings 0001318605 --type 10-K --count 5
    python main.py company us_ca C0806592
"""

import argparse
import json
import os

from config import OUTPUT_DIR
from lookup import (
    search_opencorporates,
    get_opencorporates_company,
    search_sec_companies,
    get_sec_filings,
    search_uk_companies,
)


def cmd_search(args):
    """Search for a business entity."""
    query = args.query
    source = args.source

    results = []

    if source in ("all", "opencorporates"):
        print(f"Searching OpenCorporates: '{query}' (jurisdiction: {args.jurisdiction})...")
        oc_results = search_opencorporates(query, jurisdiction=args.jurisdiction)
        results.extend(oc_results)
        print(f"  → {len(oc_results)} results")

    if source in ("all", "sec"):
        print(f"Searching SEC EDGAR: '{query}'...")
        sec_results = search_sec_companies(query)
        results.extend(sec_results)
        print(f"  → {len(sec_results)} results")

    if source in ("all", "uk"):
        print(f"Searching UK Companies House: '{query}'...")
        uk_results = search_uk_companies(query)
        results.extend(uk_results)
        print(f"  → {len(uk_results)} results")

    if not results:
        print("No results found.")
        return

    print(f"\nTotal: {len(results)} results\n")
    for i, r in enumerate(results[:30], 1):
        src = r.get("source", "?")
        status = r.get("status", "")
        status_str = f" [{status}]" if status else ""
        print(f"{i:3}. [{src}] {r.get('name', 'N/A')}{status_str}")
        if r.get("company_number"):
            print(f"     Number: {r['company_number']}  Jurisdiction: {r.get('jurisdiction', '')}")
        if r.get("ticker"):
            print(f"     Ticker: {r['ticker']}  CIK: {r.get('cik', '')}")
        if r.get("address"):
            print(f"     Address: {r['address'][:80]}")
        if r.get("incorporation_date"):
            print(f"     Incorporated: {r['incorporation_date']}")
        print()

    _save_results(results, f"search_{query.replace(' ', '_')}.json")


def cmd_filings(args):
    """Get SEC filings for a company."""
    print(f"Fetching SEC filings for CIK {args.cik} (type: {args.type})...\n")

    filings = get_sec_filings(args.cik, filing_type=args.type, count=args.count)

    if not filings:
        print("No filings found.")
        return

    print(f"Found {len(filings)} filings:\n")
    for i, f in enumerate(filings, 1):
        print(f"{i:3}. {f['form']:8s}  {f['date']}  {f['url']}")

    _save_results(filings, f"filings_{args.cik}.json")


def cmd_company(args):
    """Get company details from OpenCorporates."""
    print(f"Fetching: {args.jurisdiction}/{args.number}...")

    company = get_opencorporates_company(args.jurisdiction, args.number)

    if not company:
        print("Company not found.")
        return

    print()
    for key, value in company.items():
        if value and key != "source":
            print(f"  {key:25s}: {value}")


def _save_results(data, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\nSaved to {filepath}")


def main():
    parser = argparse.ArgumentParser(description="US/UK Business Entity & SEC Filing Lookup")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # search
    sp = subparsers.add_parser("search", help="Search for a business entity")
    sp.add_argument("query", help="Company name or ticker")
    sp.add_argument("--source", default="all", choices=["all", "opencorporates", "sec", "uk"],
                    help="Data source (default: all)")
    sp.add_argument("--jurisdiction", default="us",
                    help="Jurisdiction code for OpenCorporates (us, gb, us_ca, us_ny, de, fr)")

    # filings
    sp = subparsers.add_parser("filings", help="Get SEC filings by CIK")
    sp.add_argument("cik", help="SEC CIK number")
    sp.add_argument("--type", default="10-K", help="Filing type (10-K, 10-Q, 8-K)")
    sp.add_argument("--count", type=int, default=10, help="Number of filings")

    # company
    sp = subparsers.add_parser("company", help="Get company details from OpenCorporates")
    sp.add_argument("jurisdiction", help="Jurisdiction (us_ca, gb, de)")
    sp.add_argument("number", help="Company registration number")

    args = parser.parse_args()

    if args.command == "search":
        cmd_search(args)
    elif args.command == "filings":
        cmd_filings(args)
    elif args.command == "company":
        cmd_company(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
