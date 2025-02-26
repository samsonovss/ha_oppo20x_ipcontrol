"""Oppo UDP-20x Telnet integration for Home Assistant.

Custom component for controlling Oppo UDP-20x series media players (e.g., UDP-203, UDP-205) via Telnet.
"""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant

DOMAIN = "oppo_telnet"  # Оставляем для совместимости с HACS и структурой
PLATFORMS = ["media_player"]

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Oppo UDP-20x Telnet component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Oppo UDP-20x Telnet from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = entry.data

    async def on_hass_stop(event):
        """Clean up when HA stops for Oppo UDP-20x Telnet."""
        _LOGGER.debug("Home Assistant is stopping, cleaning up Oppo UDP-20x Telnet")

    entry.async_on_unload(
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, on_hass_stop)
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload an Oppo UDP-20x Telnet config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
