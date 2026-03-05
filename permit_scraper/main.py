"""US Building Permit Scraper — main CLI.

Usage:
    python main.py fetch new_york_city --days 7 --limit 100
    python main.py fetch chicago --type SOLAR --days 30
    python main.py fetch-all --days 14 --limit 200
    python main.py cities
    python main.py stats new_york_city --days 30
"""

import argparse
import json
import os
from collections import Counter

from config import OUTPUT_DIR, PERMIT_SOURCES
from scraper import fetch_permits, fetch_all_cities


def cmd_fetch(args):
    """Fetch permits from a single city."""
    print(f"Fetching permits: {args.city} (last {args.days} days, limit {args.limit})")

    permits = fetch_permits(
        args.city,
        limit=args.limit,
        days_back=args.days,
        permit_type=args.type,
        app_token=args.token,
    )

    if not permits:
        print("No permits found.")
        return

    print(f"\nFound {len(permits)} permits:\n")
    for i, p in enumerate(permits[:20], 1):
        cost = p["estimated_cost"]
        cost_str = f"${cost}" if cost else "N/A"
        print(f"{i:3}. {p['permit_number'] or 'N/A':20s} | {p['permit_type'][:15]:15s} | {cost_str:>12s}")
        print(f"     {p['address'][:60]}")
        if p["description"]:
            print(f"     {p['description'][:80]}")
        print()

    if len(permits) > 20:
        print(f"... and {len(permits) - 20} more\n")

    _save_results(permits, f"permits_{args.city}.json")


def cmd_fetch_all(args):
    """Fetch permits from all configured cities."""
    print(f"Fetching from all {len(PERMIT_SOURCES)} cities (last {args.days} days)...\n")

    all_permits = fetch_all_cities(
        days_back=args.days,
        limit_per_city=args.limit,
        app_token=args.token,
    )

    # Flatten for export
    flat = []
    for city_permits in all_permits.values():
        flat.extend(city_permits)

    _save_results(flat, "permits_all.json")

    # Summary
    print("\nSummary by city:")
    for city_key, permits in sorted(all_permits.items(), key=lambda x: -len(x[1])):
        source = PERMIT_SOURCES[city_key]
        print(f"  {source['name']:25s} {len(permits):5d} permits")


def cmd_cities(args):
    """List available cities."""
    print(f"Available cities ({len(PERMIT_SOURCES)}):\n")
    for key, src in PERMIT_SOURCES.items():
        print(f"  {key:25s} {src['name']:20s} {src['state']:5s} ({src['api_type']})")
    print(f"\nUsage: python main.py fetch <city_key> --days 30")


def cmd_stats(args):
    """Show permit statistics for a city."""
    print(f"Fetching stats for {args.city} (last {args.days} days)...\n")

    permits = fetch_permits(
        args.city,
        limit=args.limit,
        days_back=args.days,
        app_token=args.token,
    )

    if not permits:
        print("No permits found.")
        return

    print(f"Total permits: {len(permits)}\n")

    # By type
    type_counts = Counter(p["permit_type"] or "Unknown" for p in permits)
    print("By permit type:")
    for ptype, count in type_counts.most_common(15):
        print(f"  {ptype:30s} {count:5d}")

    # By status
    status_counts = Counter(p["status"] or "Unknown" for p in permits)
    print("\nBy status:")
    for status, count in status_counts.most_common(10):
        print(f"  {status:30s} {count:5d}")

    # Cost stats
    costs = []
    for p in permits:
        try:
            cost = float(p["estimated_cost"].replace(",", "").replace("$", ""))
            if cost > 0:
                costs.append(cost)
        except (ValueError, AttributeError):
            pass

    if costs:
        print(f"\nEstimated cost stats ({len(costs)} permits with cost data):")
        print(f"  Total:   ${sum(costs):>15,.0f}")
        print(f"  Average: ${sum(costs)/len(costs):>15,.0f}")
        print(f"  Median:  ${sorted(costs)[len(costs)//2]:>15,.0f}")
        print(f"  Max:     ${max(costs):>15,.0f}")


def _save_results(data: list, filename: str):
    """Save results to JSON file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Strip raw field for export
    clean = [{k: v for k, v in r.items() if k != "raw"} for r in data]
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, default=str)
    print(f"Saved to {filepath}")


def main():
    parser = argparse.ArgumentParser(description="US Building Permit Scraper")
    parser.add_argument("--token", help="Socrata app token for higher rate limits")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # fetch
    sp = subparsers.add_parser("fetch", help="Fetch permits from one city")
    sp.add_argument("city", help="City key (use 'cities' command to list)")
    sp.add_argument("--days", type=int, default=30, help="Days back (default: 30)")
    sp.add_argument("--limit", type=int, default=1000, help="Max records (default: 1000)")
    sp.add_argument("--type", help="Filter by permit type (e.g., SOLAR, DEMOLITION)")

    # fetch-all
    sp = subparsers.add_parser("fetch-all", help="Fetch from all cities")
    sp.add_argument("--days", type=int, default=30, help="Days back (default: 30)")
    sp.add_argument("--limit", type=int, default=500, help="Max per city (default: 500)")

    # cities
    subparsers.add_parser("cities", help="List available cities")

    # stats
    sp = subparsers.add_parser("stats", help="Permit statistics for a city")
    sp.add_argument("city", help="City key")
    sp.add_argument("--days", type=int, default=30, help="Days back (default: 30)")
    sp.add_argument("--limit", type=int, default=5000, help="Max records (default: 5000)")

    args = parser.parse_args()

    if args.command == "fetch":
        cmd_fetch(args)
    elif args.command == "fetch-all":
        cmd_fetch_all(args)
    elif args.command == "cities":
        cmd_cities(args)
    elif args.command == "stats":
        cmd_stats(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
