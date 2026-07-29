#!/usr/bin/env python3
"""
Extract the rental history out of every version of portsmouth-housing-snapshot.html
in git, so we can see what was measured, when, and on what basis.

Run from the repo root:
    python3 tools/extract-snapshot-history.py

Writes housing/snapshot-history.json and prints a comparison table.
Does not modify the snapshot file or make any commits.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

TARGET = "housing/portsmouth-housing-snapshot.html"
OUT = Path("housing/snapshot-history.json")

UNIT_RE = re.compile(
    r'\{\s*type:\s*"([^"]+)"\s*,\s*median:\s*(\d+)\s*,\s*min:\s*(\d+)\s*,'
    r'\s*max:\s*(\d+)\s*,\s*count:\s*(\d+)'
)
UPDATED_RE = re.compile(r'updated:\s*"([^"]+)"')
RECIPE_RE = re.compile(r'recipe_frozen:\s*"([^"]+)"')
METHODKEY_RE = re.compile(r'method:\s*"([^"]+)"')
ISO_RE = re.compile(r'updated_iso:\s*"([^"]+)"')
# the methodology comment sits between "rental:" and the units array
METHOD_RE = re.compile(r'((?:^\s*//.*\n)+)\s*rental:\s*\{', re.MULTILINE)


def sh(args):
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def main():
    try:
        log = sh(["git", "log", "--format=%H|%ad", "--date=short", "--", TARGET])
    except subprocess.CalledProcessError:
        sys.exit("Not a git repo, or run this from the repo root.")

    commits = [line.split("|") for line in log.strip().splitlines() if line.strip()]
    if not commits:
        sys.exit(f"No history found for {TARGET}")

    # oldest first
    commits.reverse()

    versions = {}   # keyed by updated_iso, last writer wins
    unparsed = []

    for sha, date in commits:
        try:
            blob = sh(["git", "show", f"{sha}:{TARGET}"])
        except subprocess.CalledProcessError:
            continue

        units = UNIT_RE.findall(blob)
        if not units:
            unparsed.append((sha, date, "no parsable units array"))
            continue

        um = UPDATED_RE.search(blob)
        im = ISO_RE.search(blob)
        iso = im.group(1) if im else date

        mm = METHOD_RE.search(blob)
        method = ""
        if mm:
            method = " ".join(
                l.strip().lstrip("/").strip() for l in mm.group(1).splitlines()
            ).strip()

        rm = RECIPE_RE.search(blob)
        mk = METHODKEY_RE.search(blob)

        versions[iso] = {
            "sha": sha,
            "commit_date": date,
            "recipe_frozen": rm.group(1) if rm else None,
            "declared_method": mk.group(1) if mk else None,
            "updated_label": um.group(1) if um else None,
            "updated_iso": iso,
            "methodology_note": method or None,
            "units": [
                {
                    "type": t,
                    "median": int(med),
                    "min": int(mn),
                    "max": int(mx),
                    "count": int(c),
                }
                for (t, med, mn, mx, c) in units
            ],
        }

    series = [versions[k] for k in sorted(versions)]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"series": series}, indent=2) + "\n", encoding="utf-8")

    # ---- printed comparison ----
    types = []
    for v in series:
        for u in v["units"]:
            if u["type"] not in types:
                types.append(u["type"])

    print(f"\n{len(series)} data cycles found in {TARGET}\n")
    header = "date".ljust(12) + "".join(t[:9].rjust(11) for t in types) + "   sha"
    print(header)
    print("-" * len(header))
    prev = None
    for v in series:
        row = v["updated_iso"].ljust(12)
        for t in types:
            u = next((x for x in v["units"] if x["type"] == t), None)
            row += (f"${u['median']:,}".rjust(11) if u else "-".rjust(11))
        row += "   " + v["sha"][:7]
        print(row)
        if prev:
            gap = (
                __import__("datetime").date.fromisoformat(v["updated_iso"])
                - __import__("datetime").date.fromisoformat(prev["updated_iso"])
            ).days
            if gap < 14:
                print(f"{'':12}^ only {gap} days after previous cycle "
                      f"— too short to read as market movement")
        prev = v

    print("\nProvenance per cycle:")
    for v in series:
        if v.get("declared_method"):
            tag = "DOCUMENTED"
            note = v["declared_method"][:110]
        elif v.get("methodology_note"):
            tag = "comment only"
            note = v["methodology_note"][:110]
        else:
            tag = "UNDOCUMENTED"
            note = "no basis recorded \u2014 not usable as a data point"
        print(f"  {v['updated_iso']}  [{tag:<12}] {note}")

    documented = [v for v in series if v.get("declared_method")]
    print(f"\n{len(documented)} of {len(series)} cycles carry a declared basis.")
    if documented:
        print(f"Comparable series begins {documented[0]['updated_iso']}. "
              f"Earlier cycles must not be charted against it.")

    if unparsed:
        print("\nCommits skipped (no parsable rental data):")
        for sha, date, why in unparsed:
            print(f"  {sha[:7]} {date}  {why}")

    print(f"\nWrote {OUT}")
    print("Review the methodology column before charting anything. Cycles measured\n"
          "on different bases are not comparable to each other.\n")


if __name__ == "__main__":
    main()