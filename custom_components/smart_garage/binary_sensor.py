"""Binary sensor platform – ventilation active, actor reachable."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import callback

from .const import DOMAIN
from .controller import SmartGarageController


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up binary sensor platform."""
    ctrl: SmartGarageController = hass.data[DOMAIN][entry.entry_id]
    entities: list[BinarySensorEntity] = [ActorReachable(entry, ctrl)]
    if ctrl.vent_enabled_cfg:
        entities.append(VentActive(entry, ctrl))
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
