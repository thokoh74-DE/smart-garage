"""Diagnostics support for Smart Garage."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .controller import SmartGarageController

REDACT_KEYS = {"notify_service"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    ctrl: SmartGarageController = hass.data[DOMAIN][entry.entry_id]

    config = dict(entry.data)
    for key in REDACT_KEYS:
        if key in config:
            config[key] = "**REDACTED**"

    return {
        "config_entry": {
            "entry_id": entry.entry_id,
            "title": entry.title,
            "version": entry.version,
            "data": config,
        },
        "state_machine": {
            "door_state": ctrl.door_state,
            "sync_state": ctrl._sync_state,
            "pulse_count": ctrl._pulse_count,
            "position": ctrl.position,
            "live_position": ctrl.get_live_position(),
            "is_ventilating": ctrl.is_ventilating,
            "is_pulsing": ctrl.is_pulsing,
            "last_command": ctrl.last_command,
            "last_drive": ctrl.last_drive,
        },
        "sensors": {
            "actor_reachable": ctrl.actor_reachable,
            "closed_sensor": ctrl.closed_sensor,
            "closed_active": (
                ctrl._sensor_active(ctrl.closed_sensor, ctrl.closed_invert)
                if ctrl.closed_sensor else None
            ),
            "open_sensor": ctrl.open_sensor,
            "open_active": (
                ctrl._sensor_active(ctrl.open_sensor, ctrl.open_invert)
                if ctrl.open_sensor else None
            ),
        },
        "ventilation": {
            "enabled": ctrl.vent_enabled_cfg,
            "humidity_configured": ctrl.humidity_configured,
            "rain_configured": ctrl.rain_configured,
            "recommendation": ctrl.vent_recommendation,
            "ah_indoor": ctrl.ah_indoor,
            "ah_outdoor": ctrl.ah_outdoor,
            "ah_diff": ctrl.ah_diff,
            "dp_indoor": ctrl.dp_indoor,
            "dp_outdoor": ctrl.dp_outdoor,
            "is_raining": ctrl.is_raining,
        },
    }
