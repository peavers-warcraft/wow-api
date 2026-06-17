#!/usr/bin/env bash
# Headless Lua Language Server diagnostics (signature/type layer) for an addon. Run from
# the addon dir (where its .luarc.json lives):
#
#   ../wow-api/scripts/lsp_check.sh                 # check . at Warning level
#   ../wow-api/scripts/lsp_check.sh src Hint        # path + level
#
# Requires lua-language-server on PATH. Reads the addon's .luarc.json (hybrid Ketho +
# /papidump library). LuaLS writes a machine-readable check.json we summarise here and
# (in CI) convert to reviewdog rdjson. Exit 1 when diagnostics are found at the level.
set -uo pipefail

if ! command -v lua-language-server >/dev/null 2>&1; then
  echo "lua-language-server not found on PATH. Install it: brew install lua-language-server" >&2
  exit 127
fi

# Default the target to "." so the addon dir is the workspace ROOT — LuaLS makes the
# --check path the root, and the .luarc.json library paths (../wow-api/...) resolve from
# there. Passing a subdir (e.g. src) would re-root and break those paths.
TARGET="${1:-.}"
LEVEL="${2:-Warning}"
LOGDIR="$(pwd)/.luals-log"
CONFIG="$(pwd)/.luarc.json"
CHECK="$LOGDIR/check.json"
mkdir -p "$LOGDIR"
rm -f "$CHECK"

# This build defaults to 'pretty' (stdout); ask for JSON written to an explicit path.
args=(--check "$TARGET" --checklevel="$LEVEL" --check_format=json
      --check_out_path="$CHECK" --logpath="$LOGDIR")
[ -f "$CONFIG" ] && args+=(--configpath="$CONFIG")

lua-language-server "${args[@]}" >/dev/null 2>&1 || true

if [ ! -s "$CHECK" ] || ! grep -q '"' "$CHECK" 2>/dev/null; then
  echo "No diagnostics at level $LEVEL."
  exit 0
fi

# Summarise by diagnostic code without extra dependencies (python3 is always present).
python3 - "$CHECK" <<'PY'
import json, sys, collections
data = json.load(open(sys.argv[1]))
by_code, total = collections.Counter(), 0
for _uri, diags in data.items():
    for d in diags:
        total += 1
        by_code[d.get("code", "?")] += 1
print("%d diagnostics" % total)
print("-- by code --")
for code, n in by_code.most_common():
    print("%5d  %s" % (n, code))
PY
exit 1
