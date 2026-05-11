"""Config flow for Oppo UDP-20x IP Control Protocol integration.

Handles the configuration setup for Oppo UDP-20x series media players via
IP Control Protocol in Home Assistant.
"""
import logging
import socket

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)
DEFAULT_HOST = "192.168.1.124"


def _host_schema(default_host: str = DEFAULT_HOST) -> vol.Schema:
    """Return the host configuration schema."""
    return vol.Schema({vol.Required(CONF_HOST, default=default_host): str})


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
                return self.async_create_entry(
                    title=f"Oppo UDP-20x {host}", data={CONF_HOST: host}
                )
            except Exception as err:  # pylint: disable=broad-except
                errors["base"] = "cannot_connect"
                _LOGGER.error("Failed to connect to %s: %s", host, err)

        return self.async_show_form(
            step_id="user",
            data_schema=_host_schema(),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input=None):
        """Handle reconfiguration of an existing Oppo UDP-20x entry."""
        entry = self._get_reconfigure_entry()
        current_host = entry.options.get(
            CONF_HOST, entry.data.get(CONF_HOST, DEFAULT_HOST)
        )
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            try:
                await self.hass.async_add_executor_job(self._test_connection, host)
            except Exception as err:  # pylint: disable=broad-except
                errors["base"] = "cannot_connect"
                _LOGGER.error("Failed to connect to %s: %s", host, err)
            else:
                self.hass.config_entries.async_update_entry(
                    entry,
                    options={**entry.options, CONF_HOST: host},
                    title=f"Oppo UDP-20x {host}",
                )
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reconfigure_successful")

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_host_schema(current_host),
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Create the options flow."""
        return OppoOptionsFlow(config_entry)

    @staticmethod
    def _test_connection(host):
        """Test IP Control connection to the Oppo UDP-20x device."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect((host, 23))
        finally:
            sock.close()


class OppoOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Oppo UDP-20x IP Control."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage Oppo UDP-20x options."""
        current_host = self._config_entry.options.get(
            CONF_HOST, self._config_entry.data.get(CONF_HOST, DEFAULT_HOST)
        )
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            try:
                await self.hass.async_add_executor_job(
                    OppoTelnetConfigFlow._test_connection, host
                )
            except Exception as err:  # pylint: disable=broad-except
                errors["base"] = "cannot_connect"
                _LOGGER.error("Failed to connect to %s: %s", host, err)
            else:
                self.hass.config_entries.async_update_entry(
                    self._config_entry, title=f"Oppo UDP-20x {host}"
                )
                return self.async_create_entry(title="", data={CONF_HOST: host})

        return self.async_show_form(
            step_id="init",
            data_schema=_host_schema(current_host),
            errors=errors,
        )
