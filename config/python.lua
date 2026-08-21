-- python deps for this project

dofile("config/shared.lua")

-- append every element of "src" onto "dst"
local function extend(dst, src)
    for _, value in ipairs(src) do
        table.insert(dst, value)
    end
    return dst
end

INSTALL_REQUIRES = {
    "elasticsearch",
}
BUILD_REQUIRES = BUILD

REQUIRES = {}
extend(REQUIRES, INSTALL_REQUIRES)
extend(REQUIRES, BUILD_REQUIRES)
