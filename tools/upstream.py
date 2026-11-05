#!/usr/bin/env python3
"""Compare facts copied from other repos with their source.

A fact with "from": "OWNER/REPO#key" (or "#key|pct": 0.96 shown as 96%) must equal that repo's launch/facts.json[key] on its default branch.
Usage: upstream.py [REPO_DIR]   exit 1 on a mismatch; a source that is not published yet is only a warning
"""
import json
import pathlib
import sys
import urllib.error
import urllib.request


def main(repo):
    facts = json.loads((repo / "launch/facts.json").read_text())
    cache, bad = {}, 0
    for key, fact in facts.items():
        if "from" not in fact:
            continue
        src, upkey = fact["from"].split("#")
        upkey, _, form = upkey.partition("|")
        if src not in cache:
            url = f"https://raw.githubusercontent.com/{src}/HEAD/launch/facts.json"
            try:
                with urllib.request.urlopen(url, timeout=20) as r:
                    cache[src] = json.load(r)
            except urllib.error.HTTPError as e:
                print(f"WARN   {src}: no launch/facts.json yet ({e.code})")
                cache[src] = None
        up = cache[src]
        if up is None:
            continue
        want = str(up[upkey]["value"]) if upkey in up else None
        if want is not None and form == "pct":
            want = f"{round(float(want) * 100)}%"
        if want != str(fact["value"]):
            print(f"STALE  {key}: shows {fact['value']!r}, {fact['from']} is {want!r}")
            bad += 1
    print("upstream: all copied facts match" if not bad else f"upstream: {bad} stale, update launch/facts.json then sync.py apply")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()))
