"""EU TED Tenders Parser — main CLI.

Usage:
    python main.py search "software development" --country DE --days 14
    python main.py search --cpv 72000000 --country FR --days 7
    python main.py monitor --cpv 72000000 --country DE --interval 1800
    python main.py details "2024/S 001-000001"
    python main.py categories
"""

import argparse
import json
import os

from config import OUTPUT_DIR, CPV_CATEGORIES, EU_COUNTRIES
from parser import search_tenders, get_notice_details, monitor_new_tenders


def cmd_search(args):
    """Search EU tenders."""
    cpv = CPV_CATEGORIES.get(args.cpv, args.cpv) if args.cpv else ""

    print(f"Searching TED: query='{args.query or '*'}' cpv={cpv or 'all'} "
          f"country={args.country or 'all'} days={args.days}\n")

    result = search_tenders(
        query=args.query or "",
        cpv=cpv,
        country=args.country or "",
        days_back=args.days,
        limit=args.limit,
    )

    tenders = result["tenders"]
    total = result["total"]

    if not tenders:
        print("No tenders found.")
        return

    print(f"Found: {total} total ({len(tenders)} shown)\n")

    for i, t in enumerate(tenders[:30], 1):
        value = t["value"] or "N/A"
        country = t["country"] or "?"
        print(f"{i:3}. [{country}] {t['notice_id']}")
        print(f"     {t['title'][:100]}")
        print(f"     Buyer: {t['buyer'][:80]}")
        print(f"     Value: {value}  |  Deadline: {t['deadline']}")
        print(f"     {t['url']}")
        print()

    _save_results(tenders, "eu_tenders.json")


def cmd_monitor(args):
    """Monitor for new tenders."""
    cpv = CPV_CATEGORIES.get(args.cpv, args.cpv) if args.cpv else ""
    monitor_new_tenders(
        cpv=cpv,
        country=args.country or "",
        interval_seconds=args.interval,
    )


def cmd_details(args):
    """Get tender details."""
    print(f"Fetching details: {args.notice_id}\n")
    details = get_notice_details(args.notice_id)

    if not details:
        print("Notice not found.")
        return

    print(json.dumps(details, indent=2, default=str)[:3000])
    _save_results(details, f"notice_{args.notice_id.replace('/', '_')}.json")


def cmd_categories(args):
    """List CPV categories."""
    print("Available CPV categories:\n")
    for key, code in sorted(CPV_CATEGORIES.items()):
        print(f"  {key:20s} {code}")
    print(f"\nUsage: python main.py search --cpv it_services --country DE")

    print(f"\nAvailable countries:\n")
    for code, name in sorted(EU_COUNTRIES.items()):
        print(f"  {code}  {name}")


def _save_results(data, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"Saved to {filepath}")


def main():
    parser = argparse.ArgumentParser(description="EU TED Tenders Parser")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # search
    sp = subparsers.add_parser("search", help="Search EU tenders")
    sp.add_argument("query", nargs="?", default="", help="Free text search")
    sp.add_argument("--cpv", help="CPV code or category name (use 'categories' to list)")
    sp.add_argument("--country", help="Country code (DE, FR, IT, etc.)")
    sp.add_argument("--days", type=int, default=30, help="Days back (default: 30)")
    sp.add_argument("--limit", type=int, default=100, help="Max results (default: 100)")

    # monitor
    sp = subparsers.add_parser("monitor", help="Monitor for new tenders")
    sp.add_argument("--cpv", help="CPV code or category name")
    sp.add_argument("--country", help="Country code")
    sp.add_argument("--interval", type=int, default=3600, help="Check interval in seconds")

    # details
    sp = subparsers.add_parser("details", help="Get tender details by notice ID")
    sp.add_argument("notice_id", help="TED notice ID")

    # categories
    subparsers.add_parser("categories", help="List CPV categories and country codes")

    args = parser.parse_args()

    if args.command == "search":
        cmd_search(args)
    elif args.command == "monitor":
        cmd_monitor(args)
    elif args.command == "details":
        cmd_details(args)
    elif args.command == "categories":
        cmd_categories(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
