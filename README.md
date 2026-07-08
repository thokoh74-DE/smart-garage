# Smart Garage

🇩🇪 [Deutsche Version](README_DE.md)

<!-- Badges -->
<p align="center">

[![HACS Custom][hacs-badge]][hacs-url]
[![GitHub Release][release-badge]][release-url]
[![License][license-badge]][license-url]
[![Hassfest][hassfest-badge]][hassfest-url]
[![HACS Validation][hacs-val-badge]][hacs-val-url]
[![CodeQL][codeql-badge]][codeql-url]
[![Downloads][downloads-badge]][release-url]

</p>

<!-- Logo -->
<p align="center">
  <img src="brand/logo.png" width="300" alt="Smart Garage – Open · Close · Ventilate · Monitor"/>
</p>

<p align="center">
  <b>Home Assistant custom integration for impulse-based garage doors</b><br>
  <sub>Open · Close · Ventilate · Monitor — fully automated, fully local</sub>
</p>

<!-- HACS Install Button -->
<p align="center">
  <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=thokoh74-DE&repository=smart-garage&category=integration">
    <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open in HACS" height="40"/>
  </a>
  &nbsp;&nbsp;
  <a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=smart_garage">
    <img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Add Integration" height="40"/>
  </a>
</p>

---

## 🏠 What is Smart Garage?

Smart Garage manages **impulse-based garage doors** — the kind where a single relay press cycles through:

> **Open → Stop → Close → Stop → Open → …**

Unlike simple on/off switches, Smart Garage uses a **pulse-counting state machine** that knows exactly where your door is — even after a Home Assistant restart, even when operated by a physical button, even when stopped mid-travel.

Designed for **Homematic IP** hardware but works with **any impulse-driven garage door motor** that has a Home Assistant switch or button entity.

---

## ✨ Key Features

<table>
<tr>
<td width="60">🚪</td>
<td><b>Impulse-Based Cover</b><br>Pulse-counting state machine with sync points from limit switches. Knows the exact door state at all times.</td>
</tr>
<tr>
<td>📍</td>
<td><b>Live Position</b><br>Estimates position during movement based on travel time. Shows "Position 45%" when stopped mid-travel.</td>
</tr>
<tr>
<td>💾</td>
<td><b>State Persistence</b><br>Survives HA restarts. Restores sync state and pulse count via RestoreEntity.</td>
</tr>
<tr>
<td>🌬️</td>
<td><b>Ventilation Control</b> (optional)<br>Auto-opens door to a small gap based on absolute humidity. Respects presence and daylight. Manual switch included.</td>
</tr>
<tr>
<td>🌧️</td>
<td><b>Rain Auto-Close</b> (optional)<br>Closes the door when rain is detected. Configurable delay. Push notification before closing.</td>
</tr>
<tr>
<td>🛡️</td>
<td><b>Accidental Opening Protection</b><br>Detects when the door moves significantly beyond the ventilation gap — confirmed by the top limit switch or sustained vibration beyond a threshold — and auto-closes with notification. Triggers only when the ventilation position was reached automatically (humidity-based) or via the manual ventilation switch and the door then overshoots. Never triggers for an explicit open command (UI, service call, or physical button), even from a ventilating state.</td>
</tr>
<tr>
<td>📡</td>
<td><b>Actor Monitoring</b><br>Alerts when the control switch goes unavailable while the door is open. All entities mark as unavailable.</td>
</tr>
<tr>
<td>🔘</td>
<td><b>External Button Detection</b><br>Recognizes physical button presses and updates the state machine accordingly.</td>
</tr>
<tr>
<td>📊</td>
<td><b>Diagnostics</b><br>Full state dump downloadable from the device page. Mirror sensors for dashboard display.</td>
</tr>
<tr>
<td>🌍</td>
<td><b>Multilingual</b><br>Full German + English translations. Entity IDs always use English. Display names follow your HA language.</td>
</tr>
</table>

---

## 📋 Requirements

| Component | Required? | Purpose |
|:----------|:---------:|:--------|
| **Switch or Button entity** | ✅ Required | Triggers the garage door motor (e.g. HmIP-PCBS) |
| Limit switch — bottom | ⭐ Recommended | Confirms closed position (e.g. HmIP-FCI6 ch1) |
| Limit switch — top | ⭐ Recommended | Confirms open position (e.g. HmIP-FCI6 ch2) |
| Vibration / tilt sensor | 💡 Optional | Detects door movement + enables safety (e.g. HmIP-STV) |
| External button entity | 💡 Optional | Detects physical button presses |
| Temperature + humidity — indoor | 💡 Optional | Enables ventilation control |
| Temperature + humidity — outdoor | 💡 Optional | Enables ventilation control |
| Rain sensor | 💡 Optional | Enables rain auto-close |
| Presence entity | 💡 Optional | Ventilation only when someone is home |
| Notification service | 💡 Optional | Push notifications for safety events |

> 💡 **Graceful degradation**: The integration works with just a control switch. Each optional sensor adds capabilities. Without climate sensors → no ventilation. Without rain sensor → no rain auto-close. The entities for disabled features are simply not created.

---

## 📦 Installation

### Via HACS (recommended)

<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=thokoh74-DE&repository=smart-garage&category=integration">
  <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open in HACS"/>
</a>

**Or manually:**
1. Open HACS → **Integrations** → ⋮ → **Custom repositories**
2. URL: `https://github.com/thokoh74-DE/smart-garage`
3. Category: **Integration**
4. Search for **Smart Garage** → Install → Restart HA

### Manual Installation

1. Download the [latest release](https://github.com/thokoh74-DE/smart-garage/releases)
2. Extract and copy `custom_components/smart_garage/` to your HA `config/custom_components/`
3. Restart Home Assistant

---

## ⚙️ Configuration

<a href="https://my.home-assistant.io/redirect/config_flow_start/?domain=smart_garage">
  <img src="https://my.home-assistant.io/badges/config_flow_start.svg" alt="Add Integration"/>
</a>

**Or:** Settings → Devices & Services → Add Integration → **Smart Garage**

### 5-Step Setup Wizard

| Step | What you configure |
|:----:|:-------------------|
| **1** | **Name** (becomes device name + entity prefix), control switch, pulse timing |
| **2** | Limit switches, vibration sensor, external button — *all optional* |
| **3** | Accidental-open protection, vibration threshold, notification service |
| **4** | Enable or disable ventilation |
| **5** | Climate sensors, rain sensor, thresholds — *all optional* |

### Reconfiguration

After setup, click the ⚙️ gear icon on the integration to access the **menu-based options flow** with **4 independent sections**. Edit only what you need — no clicking through everything.

---

## 📊 Entities

### Controls

| Entity | Type | Created |
|:-------|:-----|:--------|
| *(device name)* | `cover` | Always |
| Ventilation Auto | `switch` | When ventilation is enabled |
| Rain Auto Close | `switch` | When rain sensor is configured |
| Manual Ventilation | `switch` | When ventilation is enabled |

### Sensors

| Entity | Type | Created |
|:-------|:-----|:--------|
| Ventilation Recommendation | `sensor` | When climate sensors are configured |
| Abs. Humidity Indoor | `sensor` | When climate sensors are configured |
| Abs. Humidity Outdoor | `sensor` | When climate sensors are configured |
| Dew Point Indoor | `sensor` | When climate sensors are configured |
| Dew Point Outdoor | `sensor` | When climate sensors are configured |
| Ventilation Active | `binary_sensor` | When ventilation is enabled |
| Actor Reachable | `binary_sensor` | Always |

### Diagnostics

| Entity | Type | Description |
|:-------|:-----|:------------|
| Current State | `sensor` | Human-readable state with position (e.g. "Position 45%") |
| Last Drive | `sensor` | Last state transition (translated enum) |
| Last Command | `sensor` | Last user command (translated enum) |
| Limit Switch Bottom | `sensor` | Mirrors hardware sensor state |
| Limit Switch Top | `sensor` | Mirrors hardware sensor state |
| Vibration Sensor | `sensor` | Mirrors hardware sensor state |
| Control Switch | `sensor` | Mirrors hardware sensor state |

---

## 🔧 How It Works

### The Impulse Motor Cycle

```
From CLOSED:
  Pulse 1 → OPENING    Pulse 2 → STOPPED
  Pulse 3 → CLOSING    Pulse 4 → STOPPED
  Pulse 5 → OPENING    (cycle repeats)

From OPEN:
  Pulse 1 → CLOSING    Pulse 2 → STOPPED
  Pulse 3 → OPENING    Pulse 4 → STOPPED
  Pulse 5 → CLOSING    (cycle repeats)
```

### Pulse Counting State Machine

The integration tracks two values:
- **Sync state** — last confirmed position from a limit switch (`CLOSED` or `OPEN`)
- **Pulse count** — number of pulses since the last sync

The current door state is derived as: **`sync_state + (pulse_count - 1) mod 4`**

When a limit switch fires → pulse counter resets to 0 (new sync point).

### Position Estimation

During movement: `position = elapsed_time ÷ travel_time × 100%`

Position is estimated relative to a **baseline captured at the start of each movement**, not always from 0% or 100%. This matters for repeated stop/reverse cycles: opening, stopping, then opening again continues accurately from the last known position instead of resetting the estimate to a full 0–100% traversal.

When limit switches are configured, the integration **never** assumes the door reached its end position based on time alone — it waits for sensor confirmation.

### Multi-Pulse Commands

| From → To | Pulses needed | Sequence |
|:----------|:-------------:|:---------|
| Closed → Opening | 1 | Open |
| Opening → Stopped | 1 | Stop |
| Stopped (up) → Closing | 1 | Close |
| Stopped (up) → Opening | 3 | Close → Stop → Open |
| Stopped (down) → Closing | 3 | Open → Stop → Close |
| Closing → Opening | 2 | Stop → Open |

All multi-pulse sequences are **cancellable** — pressing Stop during a sequence aborts it immediately via the command sequence counter.

---

## 🔌 Supported Hardware

### Tested With

| Device | Type | Purpose |
|:-------|:-----|:--------|
| **HmIP-PCBS** | Switching actuator | Control relay (impulse) |
| **HmIP-FCI6** | Contact interface | Limit switches (ch1 = bottom, ch2 = top) |
| **HmIP-STV** | Tilt sensor | Vibration / movement detection |

### Homematic IP Wiring Notes

| Device | Channel | Function | Invert? |
|:-------|:--------|:---------|:--------|
| HmIP-FCI6 | ch1 | Limit switch bottom | **Yes** (OFF = closed) |
| HmIP-FCI6 | ch2 | Limit switch top | **No** (ON = open) |
| HmIP-PCBS | — | Control switch | — |
| HmIP-STV | — | Vibration sensor | — |

### Compatible With

Any impulse-based garage door motor that can be controlled via a Home Assistant `switch` or `button` entity. This includes motors from Hörmann, Marantec, Chamberlain, Sommer, Novoferm, and others that use a simple impulse/toggle mechanism.

---

## 🐛 Troubleshooting

<details>
<summary><b>Entity IDs show wrong language</b></summary>

Entity IDs are generated once when entities are first created. If they have German names from a previous version, delete the integration and re-add it.
</details>

<details>
<summary><b>Homematic actor loses connection</b></summary>

Increase the **Pulse delay** setting. Homematic IP devices can lose connectivity when receiving too many RF signals in quick succession. Default is 1 second; try 2-3 seconds.
</details>

<details>
<summary><b>Wrong state after HA restart</b></summary>

The state is persisted via RestoreEntity. If incorrect, operate the door once so a limit switch fires and triggers a sync (resets pulse counter to 0).
</details>

<details>
<summary><b>Stop doesn't respond quickly</b></summary>

Fixed in v1.0: service calls use fire-and-forget (no `blocking=True`), so the stop command is processed immediately without waiting for Homematic RF confirmation.
</details>

<details>
<summary><b>Position becomes inaccurate after repeated stop/reverse cycles</b></summary>

Fixed in v1.0.3: position is now calculated relative to a baseline captured at the start of each movement, instead of always assuming travel from 0% or 100%. Update to the latest version if you still see this.
</details>

<details>
<summary><b>False "accidental opening" warning when I open the door myself</b></summary>

Fixed in v1.0.3: the safety warning no longer fires for an explicit open command (UI, service call, or physical button), even from a ventilating state. It now correctly fires only when the door overshoots past the ventilation gap after an automatic or manual ventilation trigger, without an explicit open command.
</details>

<details>
<summary><b>Need debug data?</b></summary>

Go to the device page → ⋮ → **Download diagnostics**. This creates a JSON file with the complete state machine state, sensor states, and configuration (sensitive data redacted).
</details>

---

## 🏆 Quality Scale

This integration targets the [Home Assistant Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/) **Silver** tier.

| Rule | Status |
|:-----|:------:|
| Config Flow | ✅ |
| Entity Unique ID | ✅ |
| Unique Config Entry | ✅ |
| Test Before Setup | ✅ |
| Config Entry Unloading | ✅ |
| Entity Unavailable | ✅ |
| Action Exceptions | ✅ |
| Parallel Updates | ✅ |
| Integration Owner | ✅ |
| Diagnostics | ✅ |
| Entity Translations | ✅ |
| Devices | ✅ |
| Reconfigure Flow | ✅ |

See [`quality_scale.yaml`](custom_components/smart_garage/quality_scale.yaml) for detailed status.

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a PR.

## 📄 License

[MIT](LICENSE) © Thomas

---

<!-- Badge URLs -->
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge
[hacs-url]: https://github.com/hacs/integration
[release-badge]: https://img.shields.io/github/v/release/thokoh74-DE/smart-garage?style=for-the-badge
[release-url]: https://github.com/thokoh74-DE/smart-garage/releases
[license-badge]: https://img.shields.io/github/license/thokoh74-DE/smart-garage?style=for-the-badge
[license-url]: https://github.com/thokoh74-DE/smart-garage/blob/main/LICENSE
[hassfest-badge]: https://img.shields.io/github/actions/workflow/status/thokoh74-DE/smart-garage/hassfest.yml?label=Hassfest&style=for-the-badge
[hassfest-url]: https://github.com/thokoh74-DE/smart-garage/actions/workflows/hassfest.yml
[hacs-val-badge]: https://img.shields.io/github/actions/workflow/status/thokoh74-DE/smart-garage/hacs.yml?label=HACS&style=for-the-badge
[hacs-val-url]: https://github.com/thokoh74-DE/smart-garage/actions/workflows/hacs.yml
[codeql-badge]: https://img.shields.io/github/actions/workflow/status/thokoh74-DE/smart-garage/codeql.yml?label=CodeQL&style=for-the-badge
[codeql-url]: https://github.com/thokoh74-DE/smart-garage/actions/workflows/codeql.yml
[downloads-badge]: https://img.shields.io/github/downloads/thokoh74-DE/smart-garage/total?style=for-the-badge
