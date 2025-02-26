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

SERVICE_SEND_COMMAND = "send_command"

async def async_setup_entry(hass, config_entry, async_add_entities):
    host = config_entry.data[CONF_HOST]
    player = OppoTelnetMediaPlayer(host)
    async_add_entities([player])
    hass.async_create_task(player.async_poll_status())

    # Регистрация сервиса
    async def handle_send_command(call):
        """Handle the send_command service."""
        command = call.data.get("command")
        if command == "select_hdmi_in":  # Специальная команда для HDMI In
            await player.async_select_hdmi_in()
        elif command:
            await player.async_send_custom_command(command)
    
    hass.services.async_register(DOMAIN, SERVICE_SEND_COMMAND, handle_send_command)

class OppoTelnetMediaPlayer(MediaPlayerEntity):
    def __init__(self, host):
        self._host = host
        self._port = 23
        self._state = MediaPlayerState.OFF
        self._volume = 0.0
        self._is_muted = False
        self._running = True
        self._attributes = {
            "up": "#NUP",
            "down": "#NDN",
            "left": "#NLT",
            "right": "#NRT",
            "enter": "#SEL",
            "home": "#HOM"
        }

    @property
    def unique_id(self):
        return f"oppo_telnet_{self._host}"

    @property
    def name(self):
        return f"Oppo Telnet {self._host}"

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
        )

    @property
    def device_info(self):
        return DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=self.name,
            manufacturer="Oppo",
            model="UDP-203",
        )

    @property
    def extra_state_attributes(self):
        return self._attributes

    async def _send_command(self, command, expect_response=False):
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
        await self._send_command(command, expect_response=False)
        _LOGGER.debug(f"Custom command '{command}' sent")

    async def async_set_volume_level(self, volume):
        new_volume = int(volume * 100)
        response = await self._send_command(f"#SVL {new_volume}", expect_response=True)
        if response and "@OK" in response:
            if abs(volume - self._volume) > 0.01:
                self._volume = volume
                _LOGGER.debug(f"Volume set to {self._volume}")
                self.async_write_ha_state()

    async def async_volume_up(self):
        new_volume = min(self._volume + 0.05, 1.0)
        response = await self._send_command(f"#SVL {int(new_volume * 100)}", expect_response=True)
        if response and "@OK" in response:
            self._volume = new_volume
            _LOGGER.debug(f"Volume increased to {self._volume}")
            self.async_write_ha_state()

    async def async_volume_down(self):
        new_volume = max(self._volume - 0.05, 0.0)
        response = await self._send_command(f"#SVL {int(new_volume * 100)}", expect_response=True)
        if response and "@OK" in response:
            self._volume = new_volume
            _LOGGER.debug(f"Volume decreased to {self._volume}")
            self.async_write_ha_state()

    async def async_media_play(self):
        if await self._send_command("#PLA"):
            self._state = MediaPlayerState.PLAYING
            self.async_write_ha_state()

    async def async_media_stop(self):
        if await self._send_command("#STP"):
            self._state = MediaPlayerState.IDLE
            self.async_write_ha_state()

    async def async_media_pause(self):
        if await self._send_command("#PAU"):
            self._state = MediaPlayerState.PAUSED
            self.async_write_ha_state()

    async def async_media_next_track(self):
        await self._send_command("#NXT")

    async def async_media_previous_track(self):
        await self._send_command("#PRE")

    async def async_turn_on(self):
        if await self._send_command("#PON"):
            self._state = MediaPlayerState.IDLE
            await asyncio.sleep(1)
            await self._update_volume()
            self.async_write_ha_state()

    async def async_turn_off(self):
        if await self._send_command("#POF"):
            self._state = MediaPlayerState.OFF
            self.async_write_ha_state()

    async def async_mute_volume(self, mute):
        if await self._send_command("#MUT"):
            self._is_muted = mute
            self.async_write_ha_state()

    async def async_select_hdmi_in(self):
        # Переключаемся на HDMI In: дважды #SRC
        for _ in range(2):
            if await self._send_command("#SRC"):
                _LOGGER.debug("Source switched with #SRC")
                await asyncio.sleep(1)  # Задержка 1 секунда между переключениями
            else:
                _LOGGER.error("Failed to send #SRC")
                return
        _LOGGER.debug("HDMI In selected")
        self.async_write_ha_state()

    async def async_press_up(self):
        await self._send_command("#NUP")

    async def async_press_down(self):
        await self._send_command("#NDN")

    async def async_press_left(self):
        await self._send_command("#NLT")

    async def async_press_right(self):
        await self._send_command("#NRT")

    async def async_press_enter(self):
        await self._send_command("#SEL")

    async def async_press_home(self):
        await self._send_command("#HOM")

    async def _update_volume(self):
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
        self._running = False
