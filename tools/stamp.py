"""Stamp style.css and app.js links with a hash of their content, so browsers fetch a new copy after every change.

  python3 tools/stamp.py        rewrite the ?v= stamps in every page
  python3 tools/stamp.py check  exit 1 if a stamp is stale (CI)
"""
import hashlib
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ("style.css", "app.js")


def digest(name):
    return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()[:8]


def stamped(html, versions):
    for name, v in versions.items():
        html = re.sub(r'((?:\.\./)?%s)(\?v=[0-9a-f]+)?"' % re.escape(name), r'\1?v=%s"' % v, html)
    return html


def main():
    check = sys.argv[1:] == ["check"]
    versions = {name: digest(name) for name in ASSETS}
    stale = []
    for page in sorted(ROOT.glob("**/index.html")):
        if ".claude" in page.relative_to(ROOT).parts:
            continue
        old = page.read_text()
        new = stamped(old, versions)
        if new != old:
            stale.append(str(page.relative_to(ROOT)))
            if not check:
                page.write_text(new)
    if check and stale:
        print("stale asset stamps, run python3 tools/stamp.py:", ", ".join(stale))
        return 1
    print(("updated: " + ", ".join(stale)) if stale and not check else "stamps current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
