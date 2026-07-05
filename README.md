# Smart Garage

🇩🇪 [Deutsche Version](README_DE.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/thokoh74-DE/smart-garage)](https://github.com/thokoh74-DE/smart-garage/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<img src="brand/icon.png" width="128" alt="Smart Garage Logo"/>

A Home Assistant custom integration for **impulse-based garage doors** – the kind where a single relay press cycles through *Open → Stop → Close → Stop → Open*.

Designed for **Homematic IP** hardware (HmIP-PCBS, HmIP-FCI6, HmIP-STV) but works with any impulse-driven garage door motor.

## Features

### 🚪 Impulse-Based Cover Entity
- **Pulse-counting state machine** – accurately tracks door position by counting relay pulses from a known sync point (limit switch)
- **State persistence** across HA restarts via `RestoreEntity`
- **Live position estimation** during movement based on configured travel time
- **External pulse detection** – recognizes physical button presses and automations
- Supports `open`, `close`, `stop` and `set_position`

### 🌬️ Ventilation Control *(optional)*
- Calculates **absolute humidity** and **dew point** from temperature/humidity sensors
- Recommends ventilation when indoor moisture exceeds outdoor by a configurable threshold
- Auto-opens door to a small ventilation gap (configurable, e.g. 2s ≈ 10 cm)
- Respects **presence** (only when home) and **daylight** (sunrise to sunset)
- **Manual ventilation switch** for direct control
- Requires: indoor + outdoor temperature and humidity sensors

### 🌧️ Rain Auto-Close *(optional)*
- Automatically closes when rain is detected
- Configurable delay (default 4 min) – won't close a just-opened door
- Push notification before closing
- Requires: rain sensor (binary_sensor)

### 🛡️ Safety
- **Accidental opening protection** – detects excessive movement during ventilation via vibration sensor and auto-closes
- **Actor reachability** – alerts when control switch goes unavailable while door is open

### 📊 Diagnostics
Mirror sensors for dashboard display: limit switches, vibration sensor, control switch state, current state with position, last drive, last command

### 🌍 Internationalization
- Full **German** and **English** UI translations
- Entity IDs always use English suffixes
- Display names follow HA system language

## Requirements

| Component | Required | Purpose |
|-----------|----------|---------|
| Switch or Button entity | ✅ Yes | Triggers the garage door motor |
| Limit switch (bottom) | ⬜ Recommended | Confirms closed position |
| Limit switch (top) | ⬜ Recommended | Confirms open position |
| Vibration/tilt sensor | ⬜ Optional | Detects door movement, enables safety |
| External button entity | ⬜ Optional | Detects physical button presses |
| Temp + humidity (indoor) | ⬜ Optional | Enables ventilation control |
| Temp + humidity (outdoor) | ⬜ Optional | Enables ventilation control |
| Rain sensor | ⬜ Optional | Enables rain auto-close |
| Presence entity | ⬜ Optional | Ventilation only when home |
| Notification service | ⬜ Optional | Push notifications for events |

> **Note**: Ventilation features are only available when all four climate sensors (indoor/outdoor temp + humidity) are configured. Rain auto-close requires a rain sensor. If these sensors are not configured, the respective features and switches are simply not created.

## Installation

### HACS (recommended)
1. Open HACS → **Integrations** → ⋮ → **Custom repositories**
2. Add `https://github.com/thokoh74-DE/smart-garage` as **Integration**
3. Search for "Smart Garage" and install
4. Restart Home Assistant

### Manual
1. Copy `custom_components/smart_garage/` to your HA `config/custom_components/` folder
2. Restart Home Assistant

## Setup

**Settings → Devices & Services → Add Integration → Smart Garage**

The setup wizard has 5 steps:
1. **Basic**: Name (becomes device name + entity prefix), control switch, pulse timing
2. **Sensors**: Limit switches, vibration sensor, external button *(all optional)*
3. **Safety**: Accidental-open protection, vibration threshold, notification service
4. **Ventilation**: Enable/disable
5. **Climate sensors**: Indoor/outdoor temp + humidity, rain sensor, thresholds *(all optional)*

After setup, use the **menu-based options flow** (gear icon) to edit individual sections without clicking through all settings.

## Entities Created

| Entity | Type | Condition |
|--------|------|-----------|
| *(device name)* | `cover` | Always |
| Ventilation Auto | `switch` | Ventilation enabled |
| Rain Auto Close | `switch` | Rain sensor configured |
| Manual Ventilation | `switch` | Ventilation enabled |
| Ventilation Recommendation | `sensor` | Climate sensors configured |
| Abs. Humidity Indoor/Outdoor | `sensor` | Climate sensors configured |
| Dew Point Indoor/Outdoor | `sensor` | Climate sensors configured |
| Ventilation Active | `binary_sensor` | Ventilation enabled |
| Actor Reachable | `binary_sensor` | Always |
| Current State | `sensor` (diag) | Always |
| Last Drive / Last Command | `sensor` (diag) | Always |
| Limit Switch Bottom/Top | `sensor` (diag) | When configured |
| Vibration Sensor | `sensor` (diag) | When configured |
| Control Switch | `sensor` (diag) | Always |

## How It Works

The impulse motor cycles through 4 phases per full cycle:

```
From CLOSED:  Pulse → Opening → Pulse → Stop → Pulse → Closing → Pulse → Stop → ...
From OPEN:    Pulse → Closing → Pulse → Stop → Pulse → Opening → Pulse → Stop → ...
```

The integration tracks a **sync state** (last confirmed position from a limit switch) and a **pulse counter**. The current door state is derived from `sync_state + pulse_count mod 4`.

When a limit switch fires, the counter resets to 0. If limit switches are configured, the integration **never** assumes the door reached its end position based on time alone – it waits for sensor confirmation.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Entity IDs have German names | Delete integration, remove stale entities, re-add |
| Actor loses connection | Increase pulse delay in basic settings |
| Wrong state after restart | Operate door once so a limit switch triggers a sync |
| Stop doesn't respond | Already fixed in v1.0 – no blocking service calls |

## License

[MIT](LICENSE)
