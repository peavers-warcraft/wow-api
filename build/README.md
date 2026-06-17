# build/ — generated, build-tagged API definitions

Each `build/<INTERFACE>/` holds the defs generated from an in-game `/papidump` for that
client build (e.g. `120007`). **Committed** so addons and CI validate without a live client.

    build/120007/
      wow-globals.lua        luacheck stds.wow (existence + C_*/Enum field checking)
      luals/wow-api.lua       LuaLS signatures (from APIDocumentation)
      luals/wow-globals.lua   LuaLS `any` existence stubs

Populate with:  python3 ../scripts/gen_wow_api.py  &&  python3 ../scripts/gen_luals_defs.py
(after `/papidump` + `/reload` in-game). Until then, validation falls back to the curated
list in config/luacheckrc.base.lua + config/curated-globals.lua. See ../README.md.
