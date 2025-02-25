"""Config flow for Oppo Telnet integration."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
import socket
import logging

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

class OppoTelnetConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Oppo Telnet."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            try:
                # Проверка доступности устройства
                await self.hass.async_add_executor_job(self._test_connection, host)
                return self.async_create_entry(title=f"Oppo Telnet {host}", data={CONF_HOST: host})
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
        """Test connection to the Oppo device."""
        sock = socket.socket()
        try:
            sock.connect((host, 23))
            sock.send(b"#QPW\r")
            response = sock.recv(15)
            if b"@OK" not in response:
                raise Exception("Unexpected response")
        finally:
            sock.close()
