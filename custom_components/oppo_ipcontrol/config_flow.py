"""Config flow for Oppo UDP-20x IP Control Protocol integration.

Handles the configuration setup for Oppo UDP-20x series media players via IP Control Protocol in Home Assistant.
"""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
import socket
import logging

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

class OppoTelnetConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Oppo UDP-20x IP Control."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step of Oppo UDP-20x IP Control configuration."""
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            try:
                await self.hass.async_add_executor_job(self._test_connection, host)
                return self.async_create_entry(title=f"Oppo UDP-20x {host}", data={CONF_HOST: host})
            except Exception as e:
                errors["base"] = "cannot_connect"
                _LOGGER.error(f"Failed to connect to {host}: {e}")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST, default="192.168.1.124"): str,
            }),
            errors=errors,
        )

    def _test_connection(self, host):
        """Test IP Control connection to the Oppo UDP-20x device."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Устанавливаем тайм-аут 5 секунд
        try:
            sock.connect((host, 23))
            # Просто проверяем, что соединение установлено, без ожидания ответа
        finally:
            sock.close()
