# Oppo Telnet Integration for Home Assistant

This integration allows controlling Oppo UDP-20x media players (e.g., UDP-203) via Telnet protocol.

## Features
- Play, stop, pause media
- Set volume level
- Turn on/off
- Next/previous track
- Mute/unmute

## Installation via HACS
1. Add this repository as a custom repository in HACS:
   - URL: `https://github.com/<your-username>/oppo-telnet`
   - Category: Integration
2. Install the integration.
3. Add to `configuration.yaml`:
   ```yaml
   media_player:
     - platform: oppo_telnet
       host: 192.168.1.124
