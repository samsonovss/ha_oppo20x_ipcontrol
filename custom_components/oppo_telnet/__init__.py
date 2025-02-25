"""Oppo Telnet integration for Home Assistant."""
from homeassistant.helpers import entity_registry as er
from .media_player import OppoTelnetMediaPlayer

DOMAIN = "oppo_telnet"

def setup(hass, config):
    """Set up the Oppo Telnet component via YAML."""
    if DOMAIN not in config:
        return True

    for conf in config[DOMAIN]:
        host = conf.get("host")
        if host:
            player = OppoTelnetMediaPlayer(host)
            hass.data.setdefault(DOMAIN, []).append(player)
            hass.helpers.discovery.load_platform(
                "media_player", DOMAIN, {"host": host}, config
            )
    return True
