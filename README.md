# Oppo UDP-20x Telnet

Custom Home Assistant integration for controlling Oppo UDP-20x series media players (e.g., UDP-203, UDP-205) via Telnet. Unlike the original UDP-based integration, this version uses Telnet protocol (port 23) for reliable command execution, eliminating the need for a web interface.

## Features
- **Power Control**: Turn the player on/off (`#PON`, `#POF`).
- **Volume Control**: Set volume level (0-100), increase/decrease by 5 steps, mute/unmute (`#SVL`, `#QVL`, `#MUT`).
- **Playback**: Play, stop, pause, next/previous track (`#PLA`, `#STP`, `#PAU`, `#NXT`, `#PRE`).
- **Navigation**: Up, Down, Left, Right, Enter, Home buttons.
- **Source Selection**: Switch to HDMI In or cycle sources manually.
- **Status Polling**: Real-time power and playback state updates (`#QPW`, `#QPL`).

## Attributes
The integration provides the following extra state attributes for use in automations:
- `up`: "Move cursor up"
- `down`: "Move cursor down"
- `left`: "Move cursor left"
- `right`: "Move cursor right"
- `enter`: "Select/Enter"
- `home`: "Return to home screen"
- `source_selection`: "Cycle through input sources (e.g., Disc → HDMI In → ARC)"
- `select_hdmi_in`: "Triggers dual #SRC commands to switch directly to HDMI In"

## Installation
1. **Via HACS**:
   - Add this repository as a custom repository in HACS.
   - Install "Oppo UDP-20x Telnet".
2. **Manual Installation**:
   - Copy the `oppo_telnet` folder to `/config/custom_components/`.
3. **Add Integration**:
   - Go to "Settings" → "Devices & Services" → "Add Integration".
   - Search for "Oppo UDP-20x Telnet" and configure with your device's IP (e.g., `192.168.1.124`).
4. **Restart Home Assistant**.

## Usage
- **Service Calls**: Use the `oppo_telnet.send_command` service to send commands.
  - Example: Switch to HDMI In:
    ```json
    {
      "entity_id": "media_player.oppo_telnet_192_168_1_124",
      "command": "select_hdmi_in"
    }
  - Example: Move cursor up:
    ```json
    {
      "entity_id": "media_player.oppo_telnet_192_168_1_124",
      "command": "up"
    }

Commands
A comprehensive list of Telnet commands for controlling the Oppo UDP-20x, including those used in this integration, can be found in COMMANDS.md with descriptions in English and Russian.
