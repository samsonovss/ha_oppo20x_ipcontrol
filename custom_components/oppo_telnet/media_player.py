"""Oppo Telnet Media Player."""
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

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Oppo Telnet media player from a config entry."""
    host = config_entry.data[CONF_HOST]
    player = OppoTelnetMediaPlayer(host)
    async_add_entities([player])
    hass.async_create_task(player.async_poll_status())

class OppoTelnetMediaPlayer(MediaPlayerEntity):
    """Representation of an Oppo Telnet media player."""

    def __init__(self, host):
        """Initialize the Oppo Telnet media player."""
        self._host = host
        self._port = 23
        self._state = MediaPlayerState.OFF
        self._volume = 0.0
        self._is_muted = False
        self._running = True
        self._attributes = {
            "up": "#UPP",
            "down": "#DWN",
            "left": "#LFT",
            "right": "#RGT",
            "enter": "#ENT"
        }

    @property
    def unique_id(self):
        """Return a unique ID for the device."""
        return f"oppo_telnet_{self._host}"

    @property
    def name(self):
        """Return the name of the device."""
        return f"Oppo Telnet {self._host}"

    @property
    def state(self):
        """Return the current state of the device."""
        return self._state

    @property
    def volume_level(self):
        """Return the current volume level (0..1)."""
        return self._volume

    @property
    def is_volume_muted(self):
        """Return True if volume is muted."""
        return self._is_muted

    @property
    def device_class(self):
        """Return the device class."""
        return MediaPlayerDeviceClass.TV

    @property
    def supported_features(self):
        """Return the supported features."""
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
        )

    @property
    def device_info(self):
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=self.name,
            manufacturer="Oppo",
            model="UDP-203",
        )

    @property
    def extra_state_attributes(self):
        """Return additional state attributes."""
        return self._attributes

    async def _send_command(self, command, expect_response=False):
        """Send a command to the Oppo device via Telnet with timeout."""
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

    async def async_set_volume_level(self, volume):
        """Set volume level, range 0..1."""
        new_volume = int(volume * 100)
        response = await self._send_command(f"#SVL {new_volume}", expect_response=True)
        if response and "@OK" in response:
            self._volume = volume
            self.async_write_ha_state()

    async def async_media_play(self):
        """Play media."""
        if await self._send_command("#PLA"):
            self._state = MediaPlayerState.PLAYING
            self.async_write_ha_state()

    async def async_media_stop(self):
        """Stop media."""
        if await self._send_command("#STP"):
            self._state = MediaPlayerState.IDLE
            self.async_write_ha_state()

    async def async_media_pause(self):
        """Pause media."""
        if await self._send_command("#PAU"):
            self._state = MediaPlayerState.PAUSED
            self.async_write_ha_state()

    async def async_media_next_track(self):
        """Skip to next track."""
        await self._send_command("#NXT")

    async def async_media_previous_track(self):
        """Skip to previous track."""
        await self._send_command("#PRE")

    async def async_turn_on(self):
        """Turn the media player on."""
        if await self._send_command("#PON"):
            self._state = MediaPlayerState.IDLE
            await asyncio.sleep(1)  # Даём время на включение
            await self._update_volume()
            self.async_write_ha_state()

    async def async_turn_off(self):
        """Turn the media player off."""
        if await self._send_command("#POF"):
            self._state = MediaPlayerState.OFF
            self.async_write_ha_state()

    async def async_mute_volume(self, mute):
        """Mute or unmute the volume."""
        if await self._send_command("#MUT"):
            self._is_muted = mute
            self.async_write_ha_state()

    async def async_press_up(self):
        """Press Up button."""
        await self._send_command("#UPP")

    async def async_press_down(self):
        """Press Down button."""
        await self._send_command("#DWN")

    async def async_press_left(self):
        """Press Left button."""
        await self._send_command("#LFT")

    async def async_press_right(self):
        """Press Right button."""
        await self._send_command("#RGT")

    async def async_press_enter(self):
        """Press Enter button."""
        await self._send_command("#ENT")

    async def _update_volume(self):
        """Update the current volume level from the device."""
        volume_status = await self._send_command("#VOL", expect_response=True)
        _LOGGER.debug(f"Volume status response: {volume_status}")
        if volume_status and "@OK" in volume_status:
            try:
                volume = int(volume_status.split()[-1]) / 100.0
                if abs(volume - self._volume) > 0.01:
                    self._volume = volume
                    _LOGGER.debug(f"Volume updated to {self._volume}")
                    self.async_write_ha_state()
            except (ValueError, IndexError):
                _LOGGER.warning(f"Failed to parse volume: {volume_status}")
        elif not volume_status or "@UVL" in volume_status:
            # Если #VOL не возвращает текущую громкость, пробуем получить через #SVL
            _LOGGER.debug("No valid #VOL response, trying workaround")
            # Устанавливаем текущую громкость, чтобы получить отклик
            await self._send_command(f"#SVL {int(self._volume * 100)}", expect_response=False)
            await asyncio.sleep(1)
            volume_status = await self._send_command("#VOL", expect_response=True)
            _LOGGER.debug(f"Retry volume status response: {volume_status}")
            if volume_status and "@OK" in volume_status:
                try:
                    volume = int(volume_status.split()[-1]) / 100.0
                    self._volume = volume
                    _LOGGER.debug(f"Volume updated to {self._volume} via workaround")
                    self.async_write_ha_state()
                except (ValueError, IndexError):
                    _LOGGER.warning(f"Failed to parse retry volume: {volume_status}")

    async def async_poll_status(self):
        """Poll the device status periodically."""
        # Инициализация при старте
        power_status = await self._send_command("#QPW", expect_response=True)
        _LOGGER.debug(f"Initial power status response: {power_status}")
        if power_status and "@OK" in power_status:
            if "ON" in power_status.upper():
                self._state = MediaPlayerState.IDLE
                await self._update_volume()  # Считываем громкость при старте
                self.async_write_ha_state()
            elif "OFF" in power_status.upper():
                self._state = MediaPlayerState.OFF
                self.async_write_ha_state()

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
        """Clean up when entity is removed."""
        self._running = False
