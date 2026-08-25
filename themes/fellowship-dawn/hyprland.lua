-- Fellowship Dawn — gilt running to oak-gall ink, with the soft shadow a
-- page casts when it is lying on another page.
local active_border_color = { colors = { "rgba(9E6F22ee)", "rgba(6B4B2Fee)" }, angle = 45 }
local inactive_border_color = "rgba(D7BF9399)"

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
      range = 14,
      render_power = 3,
      color = "rgba(6B4B2F2e)",
      color_inactive = "rgba(A08B6024)",
    },
  },
})
