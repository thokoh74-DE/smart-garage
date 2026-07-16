"""Binary sensor platform – ventilation active, actor reachable."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN
from .controller import SmartGarageController


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up binary sensor platform."""
    ctrl: SmartGarageController = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = [ActorReachable(entry, ctrl)]
    if ctrl.vent_enabled_cfg:
        entities.append(VentActive(entry, ctrl))
    if ctrl.closed_sensor:
        entities.append(
            DiagMirrorBinary(
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
            DiagMirrorBinary(
                entry,
                hass,
                ctrl,
                "limit_switch_top",
                ctrl.open_sensor,
                "endschalter_oben",
                "mdi:arrow-collapse-up",
            )
        )
    async_add_entities(entities, True)


class _BaseBinary(BinarySensorEntity):
    """Base binary sensor with device info and update callback."""

    _attr_has_entity_name = True
    _ctrl: SmartGarageController

    @property
    def device_info(self):
        """Return device info."""
        return self._ctrl.device_info

    async def async_added_to_hass(self) -> None:
        """Register update callback."""
        self._ctrl.register_update_callback(self._handle_update)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister update callback."""
        self._ctrl.unregister_update_callback(self._handle_update)

    @callback
    def _handle_update(self) -> None:
        """Handle controller state change."""
        self.async_write_ha_state()


class VentActive(_BaseBinary):
    """Shows whether the garage is currently in ventilation position."""

    _attr_device_class = BinarySensorDeviceClass.OPENING
    _attr_icon = "mdi:air-filter"
    _attr_translation_key = "ventilation_active"

    def __init__(self, entry, ctrl) -> None:
        self._ctrl = ctrl
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_vent_active"

    @property
    def is_on(self) -> bool:
        """Return True when ventilating."""
        return self._ctrl.is_ventilating


class ActorReachable(_BaseBinary):
    """Shows whether the control switch is reachable."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_icon = "mdi:lan-connect"
    _attr_translation_key = "actor_reachable"

    def __init__(self, entry, ctrl) -> None:
        self._ctrl = ctrl
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_actor_reachable"

    @property
    def is_on(self) -> bool:
        """Return True when actor is reachable."""
        return self._ctrl.actor_reachable


class DiagMirrorBinary(BinarySensorEntity):
    """Mirror another on/off entity's state under the Smart Garage device.

    Unlike the generic DiagMirror sensor (used for enum/mirror diagnostics
    that aren't strictly binary), this lives in the binary_sensor domain so
    the frontend's state_color logic (e.g. multiple-entity-row) can color
    the icon based on on/off state.
    """

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
    def is_on(self) -> bool | None:
        state = self._hass_ref.states.get(self._source_id)
        if state is None or state.state in ("unknown", "unavailable"):
            return None
        return state.state == "on"

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
