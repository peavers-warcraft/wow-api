#!/usr/bin/env python3
"""Convert a lua-language-server check.json into reviewdog rdjson (on stdout).

reviewdog reads rdjson and posts each diagnostic as an inline PR comment:
    lua-language-server --check . --check_format=json --check_out_path=check.json ...
    python3 luals_to_rdjson.py check.json BASEDIR | reviewdog -f=rdjson -reporter=github-pr-review

check.json maps "file://<abs>" -> [ {message, code, severity, range:{start:{line,character}}}, ... ]
LuaLS lines/characters are 0-based; rdjson is 1-based. Paths are emitted relative to BASEDIR
(the addon dir / repo root) so reviewdog can match them to the PR diff.
"""
import json
import os
import sys

# LuaLS numeric severity: 1=Error 2=Warning 3=Information 4=Hint
SEV = {1: "ERROR", 2: "WARNING", 3: "INFO", 4: "INFO"}


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: luals_to_rdjson.py check.json [basedir]")
    check_path = sys.argv[1]
    basedir = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.getcwd()

    diagnostics = []
    if os.path.exists(check_path) and os.path.getsize(check_path) > 0:
        data = json.load(open(check_path, encoding="utf-8"))
        # LuaLS emits a uri->diagnostics map when there are findings, but an empty list [] when
        # the workspace is clean. Only the map form has diagnostics to convert.
        for uri, diags in (data.items() if isinstance(data, dict) else []):
            path = uri[len("file://"):] if uri.startswith("file://") else uri
            rel = os.path.relpath(path, basedir)
            for d in diags:
                start = d.get("range", {}).get("start", {})
                end = d.get("range", {}).get("end", start)
                code = d.get("code", "")
                diagnostics.append({
                    "message": d.get("message", "").strip(),
                    "location": {
                        "path": rel,
                        "range": {
                            "start": {"line": start.get("line", 0) + 1,
                                      "column": start.get("character", 0) + 1},
                            "end": {"line": end.get("line", 0) + 1,
                                    "column": end.get("character", 0) + 1},
                        },
                    },
                    "severity": SEV.get(d.get("severity", 2), "WARNING"),
                    "code": {"value": code} if code else None,
                })

    out = {
        "source": {"name": "lua-language-server",
                   "url": "https://github.com/LuaLS/lua-language-server"},
        "diagnostics": [{k: v for k, v in d.items() if v is not None} for d in diagnostics],
    }
    json.dump(out, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
