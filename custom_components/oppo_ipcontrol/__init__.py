"""Oppo UDP-20x IP Control Protocol integration for Home Assistant.

Custom component for controlling Oppo UDP-20x series media players (e.g., UDP-203, UDP-205) via IP Control Protocol.
"""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant

DOMAIN = "oppo_ipcontrol" 
PLATFORMS = ["media_player"]

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Oppo UDP-20x IP Control component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Oppo UDP-20x IP Control from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        **entry.data,
        CONF_HOST: entry.options.get(CONF_HOST, entry.data.get(CONF_HOST)),
    }

    async def on_hass_stop(event):
        """Clean up when HA stops for Oppo UDP-20x IP Control."""
        _LOGGER.debug("Home Assistant is stopping, cleaning up Oppo UDP-20x IP Control")

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, on_hass_stop)
    )

    async def async_update_options(hass: HomeAssistant, updated_entry: ConfigEntry):
        """Reload the entry when options are updated."""
        await hass.config_entries.async_reload(updated_entry.entry_id)

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload an Oppo UDP-20x Telnet config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: ConfigEntry, device_entry
) -> bool:
    """Allow Home Assistant to remove stale devices for this config entry."""
    return True
