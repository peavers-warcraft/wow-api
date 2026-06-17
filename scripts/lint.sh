#!/usr/bin/env bash
# Lint an addon's Lua against the WoW API (existence layer). Run from an addon dir:
#
#   ../wow-api/scripts/lint.sh                 # check src/ + Changelog.lua
#   ../wow-api/scripts/lint.sh src/UI          # a subset
#
# Requires luacheck on PATH (brew install luacheck / apt / luarocks). Exit code is
# luacheck's own: 0 = clean, non-zero = warnings/errors (handy for CI).
set -euo pipefail

if ! command -v luacheck >/dev/null 2>&1; then
  echo "luacheck not found on PATH. Install it: brew install luacheck (macOS) or luarocks install luacheck" >&2
  exit 127
fi

# Default targets when none are passed.
if [ "$#" -gt 0 ]; then
  targets=("$@")
else
  targets=("src")
  [ -f "Changelog.lua" ] && targets+=("Changelog.lua")
fi

exec luacheck "${targets[@]}"
