#!/usr/bin/env python3
"""Convert `luacheck --formatter plain --codes` output (stdin) into reviewdog rdjson.

    luacheck src --formatter plain --codes | python3 luacheck_to_rdjson.py | \
        reviewdog -f=rdjson -reporter=github-pr-review

Plain lines look like:  src/Foo.lua:12:7: (W113) accessing undefined variable X
The code's leading letter sets severity: E* -> ERROR (syntax/fatal), W* -> WARNING.
"""
import re
import sys
import json

LINE = re.compile(r"^(.*?):(\d+):(\d+):\s*\(([EW])(\d+)\)\s*(.*)$")


def main():
    diagnostics = []
    for raw in sys.stdin:
        m = LINE.match(raw.rstrip("\n"))
        if not m:
            continue
        path, line, col, sev, num, msg = m.groups()
        diagnostics.append({
            "message": msg.strip(),
            "location": {
                "path": path,
                "range": {"start": {"line": int(line), "column": int(col)}},
            },
            "severity": "ERROR" if sev == "E" else "WARNING",
            "code": {"value": sev + num},
        })
    json.dump({
        "source": {"name": "luacheck",
                   "url": "https://github.com/lunarmodules/luacheck"},
        "diagnostics": diagnostics,
    }, sys.stdout)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
