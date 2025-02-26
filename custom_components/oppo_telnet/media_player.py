"""Oppo UDP-20x Telnet Media Player.

Custom integration for controlling Oppo UDP-20x series (e.g., UDP-203, UDP-205) via Telnet.
Supports power, volume, playback, navigation, and source selection (e.g., HDMI In).
"""
import asyncio
import socket
from homeassistant.components.media_player import MediaPlayerEntity, MediaPlayerDeviceClass
from homeassistant.components.media_player.const import (
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.const import CONF_HOST
from homeassistant.helpers.entity import DeviceInfo
import logging

DOMAIN = "oppo_telnet"
_LOGGER = logging.getLogger(__name__)

SERVICE_SEND_COMMAND = "send_command"

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Oppo UDP-20x Telnet media player from a config entry."""
    host = config_entry.data[CONF_HOST]
    player = OppoTelnetMediaPlayer(host)
    async_add_entities([player])
    hass.async_create_task(player.async_poll_status())

    async def handle_send_command(call):
        """Handle the send_command service for Oppo UDP-20x."""
        command = call.data.get("command")
        if command == "select_hdmi_in":
            await player.async_select_hdmi_in()
        elif command in player._command_map:
            await player.async_send_custom_command(player._command_map[command])
        elif command:
            await player.async_send_custom_command(command)
    
    hass.services.async_register(DOMAIN, SERVICE_SEND_COMMAND, handle_send_command)

class OppoTelnetMediaPlayer(MediaPlayerEntity):
    """Representation of an Oppo UDP-20x Telnet media player."""

    def __init__(self, host):
        self._host = host
        self._port = 23
        self._state = MediaPlayerState.OFF
        self._volume = 0.0
        self._is_muted = False
        self._running = True
        self._current_source = None
        # Внутренний словарь команд Telnet (официальные из документации)
        self._command_map = {
            "up": "#UPP",
            "down": "#DWN",
            "left": "#LFT",
            "right": "#RGT",
            "enter": "#ENT",
            "home": "#HOME",
            "source_selection": "#SRC",
            "select_hdmi_in": "select_hdmi_in"
        }
        # Атрибуты с описаниями для отображения в HA
        self._attributes = {
            "up": "Move cursor up",
            "down": "Move cursor down",
            "left": "Move cursor left",
            "right": "Move cursor right",
            "enter": "Select/Enter",
            "home": "Return to home screen",
            "source_selection": "Cycle through input sources (e.g., Disc → HDMI In → ARC)",
            "select_hdmi_in": "Switch directly to HDMI In"
        }
        # Список источников для выбора в карточке
        self._source_list = ["Disc", "HDMI In", "ARC: HDMI Out"]
        # Соответствие источников и команд #SIS
        self._source_to_command = {
            "Disc": "#SIS 0",
            "HDMI In": "#SIS 1",
            "ARC: HDMI Out": "#SIS 2"
        }

    @property
    def unique_id(self):
        return f"oppo_telnet_{self._host}"

    @property
    def name(self):
        return "Oppo UDP-20x"

    @property
    def state(self):
        return self._state

    @property
    def volume_level(self):
        return self._volume

    @property
    def is_volume_muted(self):
        return self._is_muted

    @property
    def device_class(self):
        return MediaPlayerDeviceClass.TV

    @property
    def supported_features(self):
        return (
            MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.STOP
            | MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.VOLUME_MUTE
            | MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.NEXT_TRACK
            | MediaPlayerEntityFeature.PREVIOUS_TRACK
            | MediaPlayerEntityFeature.VOLUME_STEP
            | MediaPlayerEntityFeature.SELECT_SOURCE
        )

    @property
    def source(self):
        return self._current_source

    @property
    def source_list(self):
        return self._source_list

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=self.name,
            manufacturer="Oppo",
            model="UDP-20x Series",
        )

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def _send_command(self, command, expect_response=False):
        """Send a Telnet command to the Oppo UDP-20x device."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=3
            )
            writer.write(f"{command}\r".encode())
            await asyncio.wait_for(writer.drain(), timeout=1)
            if expect_response:
                response = await asyncio.wait_for(reader.read(2048), timeout=2)
                writer.close()
                await writer.wait_closed()
                return response.decode().strip()
            writer.close()
            await writer.wait_closed()
            return True
        except asyncio.TimeoutError:
            _LOGGER.debug(f"Timeout sending command {command} to {self._host}")
            return False
        except Exception as e:
            _LOGGER.debug(f"Failed to send command {command}: {e}")
            return False

    async def async_send_custom_command(self, command):
        """Send a custom Telnet command to the Oppo UDP-20x."""
        await self._send_command(command, expect_response=False)
        _LOGGER.debug(f"Custom command '{command}' sent")

    async def async_set_volume_level(self, volume):
        """Set volume level (0-1) for Oppo UDP-20x."""
        new_volume = int(volume * 100)
        response = await self._send_command(f"#SVL {new_volume}", expect_response=True)
        if response and "@OK" in response:
            if abs(volume - self._volume) > 0.01:
                self._volume = volume
                _LOGGER.debug(f"Volume set to {self._volume}")
                self.async_write_ha_state()

    async def async_volume_up(self):
        """Increase volume for Oppo UDP-20x."""
        response = await self._send_command("#VOL +", expect_response=True)
        if response and "@OK" in response:
            # Обновляем громкость из ответа (например, @OK 45)
            try:
                volume_parts = response.split()
                if len(volume_parts) > 1 and volume_parts[1].isdigit():
                    self._volume = int(volume_parts[1]) / 100.0
                _LOGGER.debug(f"Volume increased to {self._volume}")
                self.async_write_ha_state()
            except (ValueError, IndexError):
                _LOGGER.warning(f"Failed to parse volume from response: {response}")

    async def async_volume_down(self):
        """Decrease volume for Oppo UDP-20x."""
        response = await self._send_command("#VOL -", expect_response=True)
        if response and "@OK" in response:
            # Обновляем громкость из ответа
            try:
                volume_parts = response.split()
                if len(volume_parts) > 1 and volume_parts[1].isdigit():
                    self._volume = int(volume_parts[1]) / 100.0
                _LOGGER.debug(f"Volume decreased to {self._volume}")
                self.async_write_ha_state()
            except (ValueError, IndexError):
                _LOGGER.warning(f"Failed to parse volume from response: {response}")

    async def async_media_play(self):
        """Play media on Oppo UDP-20x."""
        if await self._send_command("#PLAY"):
            self._state = MediaPlayerState.PLAYING
            self.async_write_ha_state()

    async def async_media_stop(self):
        """Stop media on Oppo UDP-20x."""
        if await self._send_command("#STOP"):
            self._state = MediaPlayerState.IDLE
            self.async_write_ha_state()

    async def async_media_pause(self):
        """Pause media on Oppo UDP-20x."""
        if await self._send_command("#PAUS"):
            self._state = MediaPlayerState.PAUSED
            self.async_write_ha_state()

    async def async_media_next_track(self):
        """Skip to next track on Oppo UDP-20x."""
        await self._send_command("#NEXT")

    async def async_media_previous_track(self):
        """Skip to previous track on Oppo UDP-20x."""
        await self._send_command("#PREV")

    async def async_turn_on(self):
        """Turn on the Oppo UDP-20x."""
        if await self._send_command("#POWER"):
            self._state = MediaPlayerState.IDLE
            await asyncio.sleep(1)
            await self._update_volume()
            self.async_write_ha_state()

    async def async_turn_off(self):
        """Turn off the Oppo UDP-20x."""
        if await self._send_command("#POWER"):
            self._state = MediaPlayerState.OFF
            self.async_write_ha_state()

    async def async_mute_volume(self, mute):
        """Mute or unmute the Oppo UDP-20x volume."""
        if await self._send_command("#MUT"):
            self._is_muted = mute
            self.async_write_ha_state()

    async def async_select_hdmi_in(self):
        """Switch Oppo UDP-20x to HDMI In source (legacy method)."""
        if await self._send_command("#SIS 1"):
            _LOGGER.debug("HDMI In selected with #SIS 1")
            self._current_source = "HDMI In"
            self.async_write_ha_state()
        else:
            _LOGGER.error("Failed to send #SIS 1")

    async def async_select_source(self, source):
        """Select source on Oppo UDP-20x."""
        if source in self._source_to_command:
            command = self._source_to_command[source]
            if await self._send_command(command):
                _LOGGER.debug(f"Source switched to {source} with {command}")
                self._current_source = source
                self.async_write_ha_state()
            else:
                _LOGGER.error(f"Failed to send {command} for source {source}")
        else:
            _LOGGER.error(f"Unknown source: {source}")

    async def async_press_up(self):
        """Press Up button on Oppo UDP-20x."""
        await self._send_command("#UPP")

    async def async_press_down(self):
        """Press Down button on Oppo UDP-20x."""
        await self._send_command("#DWN")

    async def async_press_left(self):
        """Press Left button on Oppo UDP-20x."""
        await self._send_command("#LFT")

    async def async_press_right(self):
        """Press Right button on Oppo UDP-20x."""
        await self._send_command("#RGT")

    async def async_press_enter(self):
        """Press Enter button on Oppo UDP-20x."""
        await self._send_command("#ENT")

    async def async_press_home(self):
        """Press Home button on Oppo UDP-20x."""
        await self._send_command("#HOME")

    async def _update_volume(self):
        """Update the current volume level from Oppo UDP-20x."""
        volume_status = await self._send_command("#QVL", expect_response=True)
        _LOGGER.debug(f"Volume status response: {volume_status}")
        if volume_status and ("@OK" in volume_status or "@UVL" in volume_status):
            try:
                volume_parts = volume_status.split()
                volume = int(volume_parts[-1]) / 100.0
                if abs(volume - self._volume) > 0.01:
                    self._volume = volume
                    _LOGGER.debug(f"Volume updated to {self._volume}")
                    self.async_write_ha_state()
            except (ValueError, IndexError):
                _LOGGER.warning(f"Failed to parse volume: {volume_status}")
        else:
            _LOGGER.debug("No valid volume response, skipping update")

    async def async_poll_status(self):
        """Poll the Oppo UDP-20x status periodically."""
        while self._running:
            try:
                power_status = await self._send_command("#QPW", expect_response=True)
                _LOGGER.debug(f"Power status response: {power_status}")
                if power_status:
                    if "ON" in power_status.upper():
                        if self._state == MediaPlayerState.OFF:
                            self._state = MediaPlayerState.IDLE
                            await self._update_volume()
                            self.async_write_ha_state()
                    elif "OFF" in power_status.upper() and self._state != MediaPlayerState.OFF:
                        self._state = MediaPlayerState.OFF
                        self.async_write_ha_state()
                else:
                    if self._state != MediaPlayerState.OFF:
                        self._state = MediaPlayerState.OFF
                        self.async_write_ha_state()

                if self._state != MediaPlayerState.OFF:
                    await self._update_volume()
                    play_status = await self._send_command("#QPL", expect_response=True)
                    _LOGGER.debug(f"Play status response: {play_status}")
                    if play_status and "@OK" in play_status:
                        status = play_status.split()[-1].lower()
                        if "play" in status and self._state != MediaPlayerState.PLAYING:
                            self._state = MediaPlayerState.PLAYING
                            self.async_write_ha_state()
                        elif "pause" in status and self._state != MediaPlayerState.PAUSED:
                            self._state = MediaPlayerState.PAUSED
                            self.async_write_ha_state()
                        elif "stop" in status and self._state != MediaPlayerState.IDLE:
                            self._state = MediaPlayerState.IDLE
                            self.async_write_ha_state()

            except Exception as e:
                _LOGGER.error(f"Error polling status: {e}")
                if self._state != MediaPlayerState.OFF:
                    self._state = MediaPlayerState.OFF
                    self.async_write_ha_state()

            await asyncio.sleep(5)

    async def async_will_remove_from_hass(self):
        """Clean up when Oppo UDP-20x entity is removed."""
        self._running = False
