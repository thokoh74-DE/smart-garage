# Smart Garage

🇩🇪 [Deutsche Version](README_DE.md)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/thokoh74-DE/smart-garage?style=for-the-badge)](https://github.com/thokoh74-DE/smart-garage/releases)
[![License](https://img.shields.io/github/license/thokoh74-DE/smart-garage?style=for-the-badge)](LICENSE)
[![Hassfest](https://img.shields.io/github/actions/workflow/status/thokoh74-DE/smart-garage/hassfest.yml?label=Hassfest&style=for-the-badge)](https://github.com/thokoh74-DE/smart-garage/actions/workflows/hassfest.yml)
[![HACS Validation](https://img.shields.io/github/actions/workflow/status/thokoh74-DE/smart-garage/hacs.yml?label=HACS&style=for-the-badge)](https://github.com/thokoh74-DE/smart-garage/actions/workflows/hacs.yml)
[![Downloads](https://img.shields.io/github/downloads/thokoh74-DE/smart-garage/total?style=for-the-badge)](https://github.com/thokoh74-DE/smart-garage/releases)

<p align="center">
  <img src="brand/logo.png" width="256" alt="Smart Garage Logo"/>
</p>

<p align="center">
  <strong>A Home Assistant custom integration for impulse-based garage doors</strong><br>
  Open · Close · Ventilate · Monitor
</p>

<p align="center">
  <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=thokoh74-DE&repository=smart-garage&category=integration">
    <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open in HACS"/>
  </a>
</p>

---

## Overview

Smart Garage manages **impulse-based garage doors** – the kind where a single relay press cycles through *Open → Stop → Close → Stop → Open*. It features a pulse-counting state machine, optional humidity-based ventilation control, rain auto-close, and comprehensive diagnostics.

Designed for **Homematic IP** hardware (HmIP-PCBS, HmIP-FCI6, HmIP-STV) but compatible with any impulse-driven garage door motor.

## Features

| Feature | Description | Required Sensors |
|---------|-------------|-----------------|
| 🚪 **Cover Control** | Open, close, stop with accurate state tracking | Control switch only |
| 📍 **Position Tracking** | Live position estimation during movement | – |
| 🔄 **Pulse Counting** | State derived from sync point + pulse count | Limit switches (recommended) |
| 💾 **State Persistence** | Survives HA restarts via RestoreEntity | – |
| 🌬️ **Ventilation** | Auto-ventilate based on absolute humidity + dew point | Temp + humidity (indoor + outdoor) |
| 🌧️ **Rain Auto-Close** | Close door when rain detected with delay | Rain sensor |
| 🛡️ **Safety** | Detect accidental opening during ventilation | Vibration sensor |
| 📡 **Actor Monitoring** | Alert when control switch goes offline | – |
| 🔘 **External Button** | Detect physical button presses | Button event entity |
| 📊 **Diagnostics** | Full state dump via HA diagnostics download | – |
| 🌍 **i18n** | Full German + English translations | – |

## Requirements

| Component | Status | Purpose |
|-----------|--------|---------|
| Switch or Button entity | **Required** | Triggers the garage door motor |
| Limit switch (bottom) | Recommended | Confirms closed position |
| Limit switch (top) | Recommended | Confirms open position |
| Vibration/tilt sensor | Optional | Movement detection + safety |
| External button entity | Optional | Physical button detection |
| Temp + humidity (indoor) | Optional | Enables ventilation |
| Temp + humidity (outdoor) | Optional | Enables ventilation |
| Rain sensor | Optional | Enables rain auto-close |
| Presence entity | Optional | Ventilation only when home |
| Notification service | Optional | Push notifications |

> Features degrade gracefully: without climate sensors → no ventilation entities. Without rain sensor → no rain auto-close. The integration works with just a control switch.

## Installation

### HACS (recommended)

[![Open in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=thokoh74-DE&repository=smart-garage&category=integration)

Or manually: HACS → Integrations → ⋮ → Custom repositories → `https://github.com/thokoh74-DE/smart-garage` → Category: Integration

### Manual
Copy `custom_components/smart_garage/` to your HA `config/custom_components/` folder and restart.

## Configuration

**Settings → Devices & Services → Add Integration → Smart Garage**

The 5-step setup wizard guides you through:
1. **Basic** – Name (becomes device prefix), control switch, pulse timing
2. **Sensors** – Limit switches, vibration sensor, external button (all optional)
3. **Safety** – Accidental-open protection, notification service
4. **Ventilation** – Enable/disable
5. **Climate** – Temp/humidity sensors, rain sensor, thresholds (all optional)

After setup: gear icon → **menu with 4 independent sections** for easy reconfiguration.

## Entities

| Entity | Type | Created When |
|--------|------|-------------|
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

```
From CLOSED:  Pulse → Opening → Pulse → Stop → Pulse → Closing → Pulse → Stop → ...
From OPEN:    Pulse → Closing → Pulse → Stop → Pulse → Opening → Pulse → Stop → ...
```

The integration tracks a **sync state** (last limit switch confirmation) and a **pulse counter**. Current state = `sync_state + pulses mod 4`. Limit switches reset the counter.

When limit switches are configured, the door state is **only** confirmed by sensors – never assumed from travel time.

## Supported Hardware

| Device | Purpose |
|--------|---------|
| HmIP-PCBS | Switching actuator (relay) |
| HmIP-FCI6 | Contact interface (limit switches) |
| HmIP-STV | Tilt/vibration sensor |
| Any impulse motor | With HA switch/button entity |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Entity IDs in wrong language | Delete integration + re-add |
| Actor loses connection | Increase pulse delay in settings |
| Wrong state after restart | Operate door once for limit switch sync |
| Need debug data | Device page → ⋮ → Download diagnostics |

## Quality Scale

This integration targets the [Home Assistant Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/) Silver tier. See `quality_scale.yaml` for detailed status.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE) © Thomas
