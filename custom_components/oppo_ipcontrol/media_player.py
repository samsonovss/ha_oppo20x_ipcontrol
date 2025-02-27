"""Oppo UDP-20x IP Control Protocol Media Player.

Custom integration for controlling Oppo UDP-20x series (e.g., UDP-203, UDP-205) via IP Control Protocol.
Supports power, volume, playback, navigation, and source selection.
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
import voluptuous as vol

DOMAIN = "oppo_ipcontrol"
_LOGGER = logging.getLogger(__name__)

# Регистрация кастомного сервиса
SERVICE_SEND_COMMAND = "send_command"

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Oppo UDP-20x IP Control Protocol media player from a config entry."""
    host = config_entry.data[CONF_HOST]
    player = OppoIPControlMediaPlayer(host)
    async_add_entities([player])
    
    # Вызываем начальную проверку состояния перед запуском периодического опроса
    await player.async_update_source_and_state()
    hass.async_create_task(player.async_poll_status())
    
    # Определение схемы данных для службы с двумя полями
    service_schema = vol.Schema({
        vol.Optional("preset_command"): str,
        vol.Optional("custom_command"): str,
    })
    
    # Регистрация сервиса с описанием параметров
    async def handle_send_command(call):
        """Handle the send_command service for Oppo UDP-20x."""
        preset_command = call.data.get("preset_command")
        custom_command = call.data.get("custom_command")
        
        # Определяем, какая команда используется
        if preset_command and preset_command in player._command_map:
            command_to_send = player._command_map[preset_command]
            _LOGGER.debug(f"Using preset command: {preset_command} -> {command_to_send}")
            await player.async_send_custom_command(command_to_send)
        elif custom_command:
            # Проверяем, что кастомная команда не пустая
            if not custom_command.strip():
                _LOGGER.warning("Custom command is empty")
                return
            
            # Добавляем #, если оно отсутствует в начале команды
            command_to_send = custom_command.strip()
            if not command_to_send.startswith("#"):
                command_to_send = f"#{command_to_send}"
            
            _LOGGER.debug(f"Using custom command: {command_to_send}")
            await player.async_send_custom_command(command_to_send)
        else:
            _LOGGER.warning("No preset or custom command provided for send_command service")
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_COMMAND,
        handle_send_command,
        schema=service_schema
    )

class OppoIPControlMediaPlayer(MediaPlayerEntity):
    """Representation of an Oppo UDP-20x IP Control Protocol media player."""

    def __init__(self, host):
        self._host = host
        self._port = 23
        self._state = MediaPlayerState.OFF
        self._volume = 0.0
        self._volume_oppo = 0  # Громкость в формате Oppo (0-100)
        self._is_muted = False
        self._running = True
        self._current_source = None
        self._last_power_command = None
        # Внутренний словарь команд IP Control Protocol (только навигация)
        self._command_map = {
            "up": "#NUP",
            "down": "#NDN",
            "left": "#NLT",
            "right": "#NRT",
            "enter": "#SEL",
            "home": "#HOM"
        }
        # Атрибуты с описаниями для отображения в HA
        self._attributes = {
            "up": "Move cursor up",
            "down": "Move cursor down",
            "left": "Move cursor left",
            "right": "Move cursor right",
            "enter": "Select/Enter",
            "home": "Return to home screen",
            "volume_level_oppo": self._volume_oppo
        }
        # Список источников для выбора в карточке
        self._state_update_pending = False  # Флаг для отслеживания ожидающих обновлений состояния
        self._source_list = ["Disc", "HDMI In", "ARC: HDMI Out"]
        # Соответствие источников и команд #SIS
        self._source_to_command = {
            "Disc": "#SIS 0",
            "HDMI In": "#SIS 1",
            "ARC: HDMI Out": "#SIS 2"
        }
        # Соответствие ответов #QIS и источников
        self._qis_to_source = {
            "0": "Disc",
            "1": "HDMI In",
            "2": "ARC: HDMI Out"
        }

    @property
    def unique_id(self):
        return f"oppo_ipcontrol_{self._host}"

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
        """Return the current source."""
        return self._current_source

    @property
    def source_list(self):
        """Return the list of available sources."""
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
        """Return the state attributes."""
        self._attributes["volume_level_oppo"] = self._volume_oppo
        return self._attributes

    async def async_update_source_and_state(self):
        """Update the device state and source at startup."""
        try:
            # Проверяем состояние питания
            power_status = await self._send_command("#QPW", expect_response=True)
            _LOGGER.debug(f"Initial power status response: {power_status}")
            
            if power_status and "ON" in power_status.upper():
                self._state = MediaPlayerState.IDLE
                # Проверяем текущий источник
                source_status = await self._send_command("#QIS", expect_response=True)
                if source_status and "@OK" in source_status:
                    try:
                        source_parts = source_status.split()
                        if len(source_parts) > 1 and source_parts[1] in self._qis_to_source:
                            self._current_source = self._qis_to_source[source_parts[1]]
                            _LOGGER.debug(f"Initial source updated to {self._current_source}")
                    except (ValueError, IndexError):
                        _LOGGER.warning(f"Failed to parse initial source from response: {source_status}")
                # Обновляем громкость
                await self._update_volume()
            else:
                self._state = MediaPlayerState.OFF
                self._current_source = None
            
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Error updating initial state and source: {e}")
            self._state = MediaPlayerState.OFF
            self._current_source = None
            self.async_write_ha_state()

    async def _send_command(self, command, expect_response=False):
        """Send an IP Control Protocol command to the Oppo UDP-20x device."""
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
        """Send a custom IP Control Protocol command to the Oppo UDP-20x."""
        await self._send_command(command, expect_response=False)
        _LOGGER.debug(f"Custom command '{command}' sent")

    async def async_set_volume_level(self, volume):
        """Set volume level (0-1) for Oppo UDP-20x."""
        new_volume = int(volume * 100)
        response = await self._send_command(f"#SVL {new_volume}", expect_response=True)
        if response and "@OK" in response:
            if abs(volume - self._volume) > 0.01:
                self._volume = volume
                self._volume_oppo = new_volume
                _LOGGER.debug(f"Volume set to {self._volume} (Oppo: {self._volume_oppo})")
                self.async_write_ha_state()

    async def async_volume_up(self):
        """Increase volume for Oppo UDP-20x."""
        response = await self._send_command("#VUP", expect_response=True)
        if response and "@OK" in response:
            try:
                volume_parts = response.split()
                if len(volume_parts) > 1 and volume_parts[1].isdigit():
                    self._volume_oppo = int(volume_parts[1])
                    self._volume = self._volume_oppo / 100.0
                    _LOGGER.debug(f"Volume increased to {self._volume} (Oppo: {self._volume_oppo})")
                    self.async_write_ha_state()
                else:
                    await self._update_volume()
            except (ValueError, IndexError):
                _LOGGER.warning(f"Failed to parse volume from response: {response}")
                await self._update_volume()
        else:
            _LOGGER.error(f"Failed to increase volume: {response}")

    async def async_volume_down(self):
        """Decrease volume for Oppo UDP-20x."""
        response = await self._send_command("#VDN", expect_response=True)
        if response and "@OK" in response:
            try:
                volume_parts = response.split()
                if len(volume_parts) > 1 and volume_parts[1].isdigit():
                    self._volume_oppo = int(volume_parts[1])
                    self._volume = self._volume_oppo / 100.0
                    _LOGGER.debug(f"Volume decreased to {self._volume} (Oppo: {self._volume_oppo})")
                    self.async_write_ha_state()
                else:
                    await self._update_volume()
            except (ValueError, IndexError):
                _LOGGER.warning(f"Failed to parse volume from response: {response}")
                await self._update_volume()
        else:
            _LOGGER.error(f"Failed to decrease volume: {response}")

    async def async_media_play(self):
        """Play media on Oppo UDP-20x."""
        if await self._send_command("#PLA"):
            self._state = MediaPlayerState.PLAYING
            self.async_write_ha_state()

    async def async_media_stop(self):
        """Stop media on Oppo UDP-20x."""
        if await self._send_command("#STP"):
            self._state = MediaPlayerState.IDLE
            self.async_write_ha_state()

    async def async_media_pause(self):
        """Pause media on Oppo UDP-20x."""
        if await self._send_command("#PAU"):
            self._state = MediaPlayerState.PAUSED
            self.async_write_ha_state()

    async def async_media_next_track(self):
        """Skip to next track on Oppo UDP-20x."""
        await self._send_command("#NXT")

    async def async_media_previous_track(self):
        """Skip to previous track on Oppo UDP-20x."""
        await self._send_command("#PRE")

    async def async_turn_on(self):
        """Turn on the Oppo UDP-20x."""
        if await self._send_command("#PON"):
            # Устанавливаем состояние включения сразу и добавляем задержку,
            # чтобы дать устройству время стабилизироваться
            self._state = MediaPlayerState.IDLE
            self._last_power_command = "on"
            _LOGGER.debug("Oppo turned on with #PON, waiting for device to settle")
            await asyncio.sleep(2)  # Увеличили задержку до 2 секунд для стабильности
            await self._update_volume()
            source_status = await self._send_command("#QIS", expect_response=True)
            if source_status and "@OK" in source_status:
                try:
                    source_parts = source_status.split()
                    if len(source_parts) > 1 and source_parts[1] in self._qis_to_source:
                        self._current_source = self._qis_to_source[source_parts[1]]
                        _LOGGER.debug(f"Current source updated to {self._current_source}")
                except (ValueError, IndexError):
                    _LOGGER.warning(f"Failed to parse source from response: {source_status}")
            self.async_write_ha_state()
        else:
            _LOGGER.error("Failed to turn on Oppo with #PON")

    async def async_turn_off(self):
        """Turn off the Oppo UDP-20x."""
        if await self._send_command("#POF"):
            # Устанавливаем состояние выключения сразу и добавляем небольшую задержку,
            # чтобы избежать ложных срабатываний опроса состояния
            self._state = MediaPlayerState.OFF
            self._current_source = None
            self._last_power_command = "off"
            _LOGGER.debug("Oppo turned off with #POF, waiting for device to settle")
            await asyncio.sleep(2)  # Увеличили задержку для стабильности
            self.async_write_ha_state()
        else:
            _LOGGER.error("Failed to turn off Oppo with #POF")

    async def async_mute_volume(self, mute):
        """Mute or unmute the Oppo UDP-20x volume."""
        if await self._send_command("#MUT"):
            self._is_muted = mute
            _LOGGER.debug(f"Mute set to {mute}")
            self.async_write_ha_state()

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
        await self._send_command("#NUP")

    async def async_press_down(self):
        """Press Down button on Oppo UDP-20x."""
        await self._send_command("#NDN")

    async def async_press_left(self):
        """Press Left button on Oppo UDP-20x."""
        await self._send_command("#NLT")

    async def async_press_right(self):
        """Press Right button on Oppo UDP-20x."""
        await self._send_command("#NRT")

    async def async_press_enter(self):
        """Press Enter button on Oppo UDP-20x."""
        await self._send_command("#SEL")

    async def async_press_home(self):
        """Press Home button on Oppo UDP-20x."""
        await self._send_command("#HOM")

    async def _update_volume(self):
        """Update the current volume level and mute status from Oppo UDP-20x."""
        volume_status = await self._send_command("#QVL", expect_response=True)
        _LOGGER.debug(f"Volume status response: {volume_status}")
        if volume_status and ("@OK" in volume_status):
            try:
                volume_parts = volume_status.split()
                if len(volume_parts) > 1:
                    if volume_parts[1] == "MUTE":
                        self._is_muted = True
                        _LOGGER.debug("Mute status updated to True")
                    elif volume_parts[1].isdigit():
                        self._is_muted = False
                        self._volume_oppo = int(volume_parts[1])
                        self._volume = self._volume_oppo / 100.0
                        _LOGGER.debug(f"Volume updated to {self._volume} (Oppo: {self._volume_oppo})")
                    self.async_write_ha_state()
            except (ValueError, IndexError):
                _LOGGER.warning(f"Failed to parse volume/mute status: {volume_status}")
        else:
            _LOGGER.debug("No valid volume response, skipping update")

    async def async_poll_status(self):
        """Poll the Oppo UDP-20x status periodically."""
        while self._running:
            try:
                # Проверяем состояние питания устройства
                power_status = await self._send_command("#QPW", expect_response=True)
                _LOGGER.debug(f"Power status response: {power_status}")
                
                if power_status:
                    if "ON" in power_status.upper():
                        if self._state == MediaPlayerState.OFF or self._state_update_pending:
                            self._state = MediaPlayerState.IDLE
                            self._state_update_pending = False
                            await self._update_volume()
                            source_status = await self._send_command("#QIS", expect_response=True)
                            if source_status and "@OK" in source_status:
                                try:
                                    source_parts = source_status.split()
                                    if len(source_parts) > 1 and source_parts[1] in self._qis_to_source:
                                        self._current_source = self._qis_to_source[source_parts[1]]
                                        _LOGGER.debug(f"Current source updated to {self._current_source}")
                                except (ValueError, IndexError):
                                    _LOGGER.warning(f"Failed to parse source from response: {source_status}")
                            self.async_write_ha_state()
                    elif "OFF" in power_status.upper():
                        # Если устройство выключено, не меняем состояние, если оно уже OFF
                        if self._state != MediaPlayerState.OFF:
                            self._state = MediaPlayerState.OFF
                            self._current_source = None  # Сбрасываем источник при выключении
                            _LOGGER.debug("Oppo confirmed as OFF")
                            self.async_write_ha_state()
                else:
                    # Если нет ответа, считаем, что устройство выключено
                    if self._state != MediaPlayerState.OFF:
                        self._state = MediaPlayerState.OFF
                        self._current_source = None
                        _LOGGER.debug("No response from #QPW, assuming Oppo is off")
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
                    self._current_source = None
                    _LOGGER.debug("Exception caught, assuming Oppo is off")
                    self.async_write_ha_state()

            await asyncio.sleep(2)

    async def async_will_remove_from_hass(self):
        """Clean up when Oppo UDP-20x entity is removed."""
        self._running = False
