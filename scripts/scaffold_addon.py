#!/usr/bin/env python3
"""Scaffold a per-addon .luacheckrc and .luarc.json that consume the shared wow-api package.

Generates the thin per-addon configs (mirroring BetterTogether's reference setup):
  <addon>/.luacheckrc  loads config/luacheckrc.base.lua, declares the addon's SavedVariables
  <addon>/.luarc.json  mirrors config/luarc.base.json (hybrid Ketho + dump + curated library)

SavedVariables are read from the addon's .toc (## SavedVariables / SavedVariablesPerCharacter).
allow_defined_top in the base means the addon's public table and SLASH_* commands need no
declaration, so SavedVariables are the only per-addon globals we must list (WoW assigns them,
so they may be read before any in-file definition).

Usage:
    python3 scripts/scaffold_addon.py ../PeaversItemLevel [../PeaversNeedThat ...]
    python3 scripts/scaffold_addon.py --all          # every sibling addon dir with a .toc
"""
import argparse
import glob
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../wow-api
MONO_ROOT = os.path.dirname(REPO_ROOT)                                     # the monorepo root


def find_toc(addon_dir):
    name = os.path.basename(os.path.normpath(addon_dir))
    # Prefer the .toc matching the addon folder name; else the first top-level .toc.
    preferred = os.path.join(addon_dir, name + ".toc")
    if os.path.exists(preferred):
        return preferred
    tocs = sorted(glob.glob(os.path.join(addon_dir, "*.toc")))
    return tocs[0] if tocs else None


def saved_vars(toc_path):
    out = []
    with open(toc_path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = re.match(r"##\s*SavedVariables(?:PerCharacter)?\s*:\s*(.+)", line, re.I)
            if m:
                out.extend(v.strip() for v in m.group(1).split(",") if v.strip())
    # de-dupe, preserve order
    seen, uniq = set(), []
    for v in out:
        if v not in seen:
            seen.add(v)
            uniq.append(v)
    return uniq


LUACHECK_TMPL = '''-- {addon} luacheck config. Thin wrapper over the shared Peavers base (../wow-api).
-- The base supplies the lua51+wow standard, ignore/exclude policy, and stds.wow (WoW API:
-- generated from /papidump when present, else curated). allow_defined_top auto-accepts this
-- addon's own public table + SLASH_* commands, so only SavedVariables are declared here.
-- Run: ../wow-api/scripts/lint.sh   (override package path with WOW_API_DIR)

local apiDir = (os and os.getenv and os.getenv("WOW_API_DIR")) or "../wow-api"
local base = assert(loadfile(apiDir .. "/config/luacheckrc.base.lua"))(apiDir)

std             = base.std
ignore          = base.ignore
exclude_files   = base.exclude
max_line_length = false
codestyle       = false
allow_defined_top = base.allow_defined_top
stds.wow        = base.wow

-- base.globals (PeaversChangelogs, SlashCmdList) + this addon's SavedVariables.
globals = base.globals
for _, g in ipairs({{{savedvars}}}) do globals[#globals + 1] = g end
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("addons", nargs="*", help="addon directories")
    ap.add_argument("--all", action="store_true", help="all sibling addon dirs with a .toc")
    ap.add_argument("--force", action="store_true", help="overwrite existing configs")
    args = ap.parse_args()

    targets = list(args.addons)
    if args.all:
        for entry in sorted(os.listdir(MONO_ROOT)):
            d = os.path.join(MONO_ROOT, entry)
            if d == REPO_ROOT or not os.path.isdir(d):
                continue
            if glob.glob(os.path.join(d, "*.toc")):
                targets.append(d)
    if not targets:
        sys.exit("No addons given. Pass dirs or --all.")

    base_luarc = os.path.join(REPO_ROOT, "config", "luarc.base.json")
    with open(base_luarc, encoding="utf-8") as fh:
        luarc_content = fh.read()

    for addon_dir in targets:
        addon_dir = os.path.abspath(addon_dir)
        name = os.path.basename(addon_dir)
        toc = find_toc(addon_dir)
        if not toc:
            print("  SKIP %s (no .toc)" % name)
            continue
        svs = saved_vars(toc)
        sv_lua = ", ".join('"%s"' % v for v in svs)

        luacheck_path = os.path.join(addon_dir, ".luacheckrc")
        luarc_path = os.path.join(addon_dir, ".luarc.json")
        for path in (luacheck_path, luarc_path):
            if os.path.exists(path) and not args.force:
                print("  KEEP %s (exists; --force to overwrite)" % os.path.relpath(path, MONO_ROOT))

        if not os.path.exists(luacheck_path) or args.force:
            with open(luacheck_path, "w", encoding="utf-8") as fh:
                fh.write(LUACHECK_TMPL.format(addon=name, savedvars=sv_lua))
        if not os.path.exists(luarc_path) or args.force:
            with open(luarc_path, "w", encoding="utf-8") as fh:
                fh.write(luarc_content)
        print("  OK   %s  (SavedVariables: %s)" % (name, ", ".join(svs) or "none"))


if __name__ == "__main__":
    main()
