#!/usr/bin/env python3
"""Vendored notification-client drift gate: runs in CI, needs no workspace _shared/.

The committed vendored file (Lineuparr/notify_client.py) must hash-match the sha256
pinned in client_manifest.json. This catches a hand-edit to the vendored copy that
silently diverges from the _shared source of truth, and it catches a CRLF checkout,
which changes the hash without changing a single character of code.

To land an INTENDED client change: edit <workspace>/_shared/notify_client.py, re-vendor
the copy into every plugin that carries one, rewrite each plugin's manifest, and commit
all of it together. That is a multi-plugin change and needs sign-off first.

Exit 0 = match; exit 1 = drift or missing.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent                  # <repo>/.github/scripts -> <repo>
# Resolve the inner package by the file it must contain, not by the repository
# directory name: on GitHub the repository is Dispatcharr-Lineuparr-Plugin while the
# inner folder is Lineuparr.
INNER = next((p.parent for p in REPO_ROOT.glob("*/fuzzy_matcher.py")), REPO_ROOT / REPO_ROOT.name)
MANIFEST = HERE / "client_manifest.json"


def main() -> int:
    if not MANIFEST.exists():
        print(f"MISSING {MANIFEST.name}")
        return 1
    pins = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failed = False
    for fname, expected in sorted(pins.items()):
        path = INNER / fname
        if not path.exists():
            print(f"MISSING vendored {fname}")
            failed = True
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            print(f"DRIFT {fname}: expected {expected[:16]}..., found {actual[:16]}...")
            print("  The vendored copy was edited directly, or was checked out with CRLF.")
            failed = True
        else:
            print(f"OK {fname}: {actual[:16]}...")
    if failed:
        print("Vendored client parity gate FAILED.")
        return 1
    print("Vendored client parity gate passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
