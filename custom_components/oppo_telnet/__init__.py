"""Oppo Telnet integration for Home Assistant."""
import voluptuous as vol
from homeassistant.const import CONF_HOST
from homeassistant.helpers import config_validation as cv
from .media_player import OppoTelnetMediaPlayer

DOMAIN = "oppo_telnet"

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.All(
        cv.ensure_list,
        [vol.Schema({
            vol.Required(CONF_HOST): cv.string,
        })]
    )
}, extra=vol.ALLOW_EXTRA)

def setup(hass, config):
    """Set up the Oppo Telnet component via YAML."""
    if DOMAIN not in config:
        return True

    for conf in config[DOMAIN]:
        host = conf[CONF_HOST]
        hass.helpers.discovery.load_platform(
            "media_player", DOMAIN, {"host": host}, config
        )
    return True
