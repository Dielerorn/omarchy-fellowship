-- Fellowship — the focused window is ringed in gold leaf running to mithril,
-- and carries a warm lamp-glow, as though lit from inside a Hobbit-hole.
local active_border_color = { colors = { "rgba(D6AC5Cee)", "rgba(E7D6B6ee)" }, angle = 45 }
local inactive_border_color = "rgba(2A322Daa)"

hl.config({
  general = {
    col = {
      active_border = active_border_color,
      inactive_border = inactive_border_color,
    },
  },

  group = {
    col = {
      border_active = active_border_color,
      border_inactive = inactive_border_color,
    },
  },

  decoration = {
    shadow = {
      enabled = true,
      range = 16,
      render_power = 3,
      color = "rgba(D6AC5C38)",
      color_inactive = "rgba(0F14126b)",
    },
  },
})
