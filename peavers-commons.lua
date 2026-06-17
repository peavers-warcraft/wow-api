---@meta
-- LuaLS definition for the PeaversCommons shared framework, consumed by every Peavers
-- addon. Mirrors the namespace surface declared in PeaversCommons/src/Core/Core.lua so
-- dependent addons get existence + autocomplete for `PeaversCommons.*` and don't read it
-- as undefined. Regenerate by hand if Core.lua's exported sub-tables change.

---@class PeaversCommons
---@field name string
---@field version string
---@field Events table        # event dispatcher (RegisterEvent/SetScript wrappers)
---@field SlashCommands table
---@field Utils table         # font/locale/string helpers
---@field SupportUI table
---@field Patrons table
---@field PatronsUI table
---@field FrameCore table     # frame factory (backdrops, dragging, locking)
---@field FrameUtils table    # widget builders (checkboxes, sliders, dropdowns)
---@field ConfigUIUtils table
---@field ConfigManager table # AceDB integration
---@field ConfigRegistry table
---@field SettingsUI table
---@field BarManager table
---@field StatBar table
---@field TitleBar table
---@field BarStyles table
---@field Debug table
PeaversCommons = {}

-- Shared cross-addon changelog registry (each addon's Changelog.lua appends to it).
---@type table
PeaversChangelogs = {}

-- Ace3 library locator, embedded under PeaversCommons/Libs (excluded from linting, so
-- declared here for consumers).
---@class LibStub
---@field NewLibrary fun(self: LibStub, major: string, minor: number): table?, number
---@overload fun(major: string, silent?: boolean): table, number
LibStub = {}
