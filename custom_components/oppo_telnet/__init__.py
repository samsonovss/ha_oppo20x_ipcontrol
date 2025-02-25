"""Oppo Telnet integration for Home Assistant."""
DOMAIN = "oppo_telnet"

async def async_setup_entry(hass, config_entry):
    """Set up Oppo Telnet from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "media_player")
    )
    return True

async def async_unload_entry(hass, config_entry):
    """Unload Oppo Telnet config entry."""
    await hass.config_entries.async_forward_entry_unload(config_entry, "media_player")
    return True
