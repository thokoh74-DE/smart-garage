"""Sensor platform – ventilation + diagnostics, all names via translation_key."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.core import callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    DOMAIN,
    DOOR_CLOSED,
    DOOR_CLOSING,
    DOOR_OPEN,
    DOOR_OPENING,
    DOOR_STOPPED_DOWN,
    DOOR_STOPPED_UP,
    DOOR_VENTILATING,
)
from .controller import SmartGarageController

LAST_DRIVE_OPTIONS = [
    "closed",
    "opening",
    "open",
    "closing",
    "stopped_up",
    "stopped_down",
    "ventilating",
]
LAST_COMMAND_OPTIONS = [
    "up",
    "down",
    "stop",
    "ventilate",
    "ventilate_close",
    "manual",
    "none",
]
_STATE_LABELS = {
    "de": {
        DOOR_CLOSED: "Geschlossen",
        DOOR_OPENING: "Wird geöffnet",
        DOOR_OPEN: "Geöffnet",
        DOOR_CLOSING: "Wird geschlossen",
        DOOR_VENTILATING: "Belüftung",
    },
    "en": {
        DOOR_CLOSED: "Closed",
        DOOR_OPENING: "Opening",
        DOOR_OPEN: "Opened",
        DOOR_CLOSING: "Closing",
        DOOR_VENTILATING: "Ventilating",
    },
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensor platform."""
    ctrl: SmartGarageController = hass.data[DOMAIN][entry.entry_id]
    entities: list[SensorEntity] = [
        DiagLastDrive(entry, ctrl),
        DiagLastCommand(entry, ctrl),
        DiagCurrentState(entry, ctrl),
    ]
    if ctrl.closed_sensor:
        entities.append(
            DiagMirror(
                entry,
                hass,
                ctrl,
                "limit_switch_bottom",
                ctrl.closed_sensor,
                "endschalter_unten",
                "mdi:arrow-collapse-down",
            )
        )
    if ctrl.open_sensor:
        entities.append(
            DiagMirror(
                entry,
                hass,
                ctrl,
                "limit_switch_top",
                ctrl.open_sensor,
                "endschalter_oben",
                "mdi:arrow-collapse-up",
            )
        )
    if ctrl.vibration_sensor:
        entities.append(
            DiagMirror(
                entry,
                hass,
                ctrl,
                "vibration_sensor",
                ctrl.vibration_sensor,
                "vibration",
                "mdi:vibrate",
            )
        )
    entities.append(
        DiagMirror(
            entry,
            hass,
            ctrl,
            "control_switch_mirror",
            ctrl.control_switch,
            "schaltaktor",
            "mdi:electric-switch",
        )
    )
    if ctrl.vent_enabled_cfg and ctrl.humidity_configured:
        entities.extend(
            [
                VentRec(entry, ctrl),
                AbsHum(entry, ctrl, "indoor"),
                AbsHum(entry, ctrl, "outdoor"),
                DewPt(entry, ctrl, "indoor"),
                DewPt(entry, ctrl, "outdoor"),
            ]
        )
    async_add_entities(entities, True)


class _CtrlMixin:
    """Mixin for entities backed by the controller."""

    _ctrl: SmartGarageController

    @property
    def device_info(self):
        """Return device info."""
        return self._ctrl.device_info

    @property
    def available(self) -> bool:
        """Return True if actor is reachable."""
        return self._ctrl.actor_reachable

    async def async_added_to_hass(self):
        """Register update callback."""
        self._ctrl.register_update_callback(self._handle_update)

    async def async_will_remove_from_hass(self):
        """Unregister update callback."""
        self._ctrl.unregister_update_callback(self._handle_update)

    @callback
    def _handle_update(self):
        """Handle controller state change."""
        self.async_write_ha_state()


class DiagLastDrive(_CtrlMixin, SensorEntity):
    """Last drive state sensor."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:page-last"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = LAST_DRIVE_OPTIONS
    _attr_translation_key = "last_drive"

    def __init__(self, entry, ctrl):
        self._ctrl = ctrl
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_last_drive"

    @property
    def native_value(self):
        return self._ctrl.last_drive


class DiagLastCommand(_CtrlMixin, SensorEntity):
    """Last command sensor."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:garage-alert"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = LAST_COMMAND_OPTIONS
    _attr_translation_key = "last_command"

    def __init__(self, entry, ctrl):
        self._ctrl = ctrl
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_last_cmd"

    @property
    def native_value(self):
        return self._ctrl.last_command or "none"


class DiagCurrentState(_CtrlMixin, SensorEntity):
    """Current door state with live position."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:garage-variant"
    _attr_translation_key = "current_state"

    def __init__(self, entry, ctrl):
        self._ctrl = ctrl
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_current_state"

    @property
    def native_value(self) -> str:
        state = self._ctrl.door_state
        pos = self._ctrl.get_live_position()
        lang = "de"
        if self.hass and hasattr(self.hass.config, "language"):
            lang = "de" if self.hass.config.language.startswith("de") else "en"
        labels = _STATE_LABELS.get(lang, _STATE_LABELS["en"])
        if state in labels:
            return labels[state]
        if state in (DOOR_STOPPED_UP, DOOR_STOPPED_DOWN):
            return f"Position {pos}%"
        return state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "door_state_raw": self._ctrl.door_state,
            "position_pct": self._ctrl.get_live_position(),
            "sync_state": self._ctrl._sync_state,
            "pulse_count": self._ctrl._pulse_count,
        }


class DiagMirror(SensorEntity):
    """Mirror another entity's state under the Smart Garage device."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry, hass, ctrl, trans_key, source_id, tag, icon):
        self._source_id = source_id
        self._hass_ref = hass
        self._ctrl = ctrl
        self._unsub = None
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_{tag}"
        self._attr_icon = icon
        self._attr_translation_key = trans_key

    @property
    def device_info(self):
        return self._ctrl.device_info

    @property
    def native_value(self) -> str | None:
        state = self._hass_ref.states.get(self._source_id)
        return state.state if state else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        state = self._hass_ref.states.get(self._source_id)
        if state is None:
            return {}
        return {
            "source_entity": self._source_id,
            "last_changed": str(state.last_changed),
        }

    async def async_added_to_hass(self):
        self._unsub = async_track_state_change_event(
            self.hass,
            [self._source_id],
            self._on_change,
        )

    async def async_will_remove_from_hass(self):
        if self._unsub:
            self._unsub()

    @callback
    def _on_change(self, event):
        self.async_write_ha_state()


class VentRec(_CtrlMixin, SensorEntity):
    """Ventilation recommendation sensor."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:air-filter"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["recommend", "neutral", "not_recommend"]
    _attr_translation_key = "ventilation_recommendation"

    def __init__(self, entry, ctrl):
        self._ctrl = ctrl
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_vent_rec"

    @property
    def native_value(self) -> str:
        return self._ctrl.vent_recommendation

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        c = self._ctrl
        return {
            "ah_indoor": c.ah_indoor,
            "ah_outdoor": c.ah_outdoor,
            "ah_diff": c.ah_diff,
            "dp_indoor": c.dp_indoor,
            "dp_outdoor": c.dp_outdoor,
            "is_raining": c.is_raining,
        }


class AbsHum(_CtrlMixin, SensorEntity):
    """Calculated absolute humidity sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "g/m³"
    _attr_icon = "mdi:water"

    def __init__(self, entry, ctrl, loc):
        self._ctrl = ctrl
        self._loc = loc
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_ah_{loc}"
        self._attr_translation_key = f"abs_humidity_{loc}"

    @property
    def native_value(self) -> float | None:
        return self._ctrl.ah_indoor if self._loc == "indoor" else self._ctrl.ah_outdoor


class DewPt(_CtrlMixin, SensorEntity):
    """Calculated dew point sensor."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_icon = "mdi:thermometer-water"

    def __init__(self, entry, ctrl, loc):
        self._ctrl = ctrl
        self._loc = loc
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_dp_{loc}"
        self._attr_translation_key = f"dew_point_{loc}"

    @property
    def native_value(self) -> float | None:
        return self._ctrl.dp_indoor if self._loc == "indoor" else self._ctrl.dp_outdoor
