"""Run: python -m cybershield.cli --demo --format html --output demo-report.html"""
from __future__ import annotations
import argparse
import sys
from .scanner import ScanError, demo_result, scan
from .reports import to_html, to_json, write_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CyberShield passive website configuration audit")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--url", help="A website you own or are authorized to check")
    target.add_argument("--demo", action="store_true", help="Use offline simulated findings")
    parser.add_argument("--format", choices=["text", "json", "html"], default="text")
    parser.add_argument("--output", help="Save a report to this path (json or html)")
    parser.add_argument("--skip-cors", action="store_true", help="Skip the optional Origin probe")
    parser.add_argument("--authorized", action="store_true", help="Confirm permission to audit --url")
    args = parser.parse_args(argv)
    if args.url and not args.authorized:
        parser.error("Live scans require --authorized (you own the site or have permission).")
    if args.output and args.format == "text":
        parser.error("For --output, select --format json or --format html.")
    try:
        result = demo_result() if args.demo else scan(args.url, test_cors=not args.skip_cors)
        if args.output:
            write_report(result, args.output, kind=args.format)
            print(f"Saved {'simulated demo' if result.demo else 'audit'} report: {args.output}")
        elif args.format == "json":
            print(to_json(result))
        elif args.format == "html":
            print(to_html(result))
        else:
            prefix = "[OFFLINE DEMO - SIMULATED] " if result.demo else ""
            print(f"{prefix}CyberShield | {result.final_url}")
            print(f"Score: {result.score}/100 ({result.grade}) | HTTP {result.http_status}")
            for finding in result.findings:
                print(f"  {finding.status:4} [{finding.severity}] {finding.title}: {finding.detail}")
                if finding.status == "WARN":
                    print(f"       Recommendation: {finding.recommendation}")
        return 0
    except (ScanError, OSError, ValueError) as exc:
        print(f"CyberShield error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
