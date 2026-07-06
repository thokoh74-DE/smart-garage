"""Switch platform – ventilation auto, rain auto close, manual ventilation."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .controller import SmartGarageController


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up switch platform."""
    ctrl: SmartGarageController = hass.data[DOMAIN][entry.entry_id]
    entities: list[SwitchEntity] = []
    if ctrl.vent_enabled_cfg:
        entities.append(VentAutoSwitch(entry, ctrl))
        entities.append(ManualVentSwitch(entry, ctrl))
    if ctrl.rain_configured:
        entities.append(RainAutoSwitch(entry, ctrl))
    if entities:
        async_add_entities(entities, True)


class _BaseSwitch(RestoreEntity, SwitchEntity):
    """Base switch with device info and availability."""

    _attr_has_entity_name = True
    _ctrl: SmartGarageController

    @property
    def device_info(self):
        """Return device info."""
        return self._ctrl.device_info

    @property
    def available(self) -> bool:
        """Return True if actor is reachable."""
        return self._ctrl.actor_reachable


class VentAutoSwitch(_BaseSwitch):
    """Toggle for automatic ventilation control."""

    _attr_icon = "mdi:fan-auto"
    _attr_translation_key = "ventilation_auto"

    def __init__(self, entry, ctrl) -> None:
        self._ctrl = ctrl
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_sw_vent"
        self._is_on = False

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_added_to_hass(self) -> None:
        last = await self.async_get_last_state()
        if last and last.state == "on":
            self._is_on = True
        self._ctrl.sw_ventilation_auto = self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        self._is_on = True
        self._ctrl.sw_ventilation_auto = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._is_on = False
        self._ctrl.sw_ventilation_auto = False
        self.async_write_ha_state()
        if self._ctrl.is_ventilating:
            await self._ctrl.async_close_ventilation()


class RainAutoSwitch(_BaseSwitch):
    """Toggle for automatic closing on rain."""

    _attr_icon = "mdi:weather-pouring"
    _attr_translation_key = "rain_auto_close"

    def __init__(self, entry, ctrl) -> None:
        self._ctrl = ctrl
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_sw_rain"
        self._is_on = False

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_added_to_hass(self) -> None:
        last = await self.async_get_last_state()
        if last and last.state == "on":
            self._is_on = True
        self._ctrl.sw_rain_auto_close = self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        self._is_on = True
        self._ctrl.sw_rain_auto_close = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._is_on = False
        self._ctrl.sw_rain_auto_close = False
        self.async_write_ha_state()


class ManualVentSwitch(_BaseSwitch):
    """Toggle to manually open/close ventilation position."""

    _attr_icon = "mdi:garage-open-variant"
    _attr_translation_key = "manual_ventilation"

    def __init__(self, entry, ctrl) -> None:
        self._ctrl = ctrl
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_sw_manual_vent"

    @property
    def is_on(self) -> bool:
        return self._ctrl.is_ventilating

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._ctrl.register_update_callback(self._handle_update)

    async def async_will_remove_from_hass(self) -> None:
        self._ctrl.unregister_update_callback(self._handle_update)

    @callback
    def _handle_update(self) -> None:
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        self._ctrl.sw_manual_ventilation = True
        await self._ctrl.async_set_manual_ventilation(True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._ctrl.sw_manual_ventilation = False
        await self._ctrl.async_set_manual_ventilation(False)
        self.async_write_ha_state()
