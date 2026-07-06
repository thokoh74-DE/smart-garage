"""Cover platform with state persistence, availability, and error handling."""

from __future__ import annotations

import json
from typing import Any

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.restore_state import RestoreEntity

from .const import (
    DOMAIN,
    DOOR_CLOSED,
    DOOR_CLOSING,
    DOOR_OPEN,
    DOOR_OPENING,
    DOOR_VENTILATING,
)
from .controller import SmartGarageController

# Phase 2.4: Prevent concurrent cover commands
PARALLEL_UPDATES = 1


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the cover platform."""
    ctrl: SmartGarageController = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SmartGarageCover(entry, ctrl)], True)


class SmartGarageCover(RestoreEntity, CoverEntity):
    """Cover entity for impulse-based garage door."""

    _attr_device_class = CoverDeviceClass.GARAGE
    _attr_has_entity_name = True

    def __init__(self, entry, ctrl: SmartGarageController) -> None:
        """Initialize the cover."""
        self._ctrl = ctrl
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_cover"
        self._attr_name = None

    @property
    def device_info(self):
        """Return device info."""
        return self._ctrl.device_info

    # Phase 2.1: Entity availability
    @property
    def available(self) -> bool:
        """Return True if the actor is reachable."""
        return self._ctrl.actor_reachable

    async def async_added_to_hass(self) -> None:
        """Restore state and register callback."""
        last = await self.async_get_last_state()
        if last and last.attributes:
            rd = last.attributes.get("_restore_data")
            if rd:
                try:
                    data = json.loads(rd) if isinstance(rd, str) else rd
                    self._ctrl.restore_state(data)
                except (json.JSONDecodeError, TypeError):
                    pass
        self._ctrl.register_update_callback(self._upd)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister callback."""
        self._ctrl.unregister_update_callback(self._upd)

    @callback
    def _upd(self) -> None:
        """Handle controller state update."""
        self.async_write_ha_state()

    @property
    def supported_features(self) -> CoverEntityFeature:
        """Return supported features."""
        return (
            CoverEntityFeature.OPEN
            | CoverEntityFeature.CLOSE
            | CoverEntityFeature.STOP
            | CoverEntityFeature.SET_POSITION
        )

    @property
    def is_closed(self) -> bool | None:
        """Return True if the cover is closed."""
        s = self._ctrl.door_state
        if s == DOOR_CLOSED:
            return True
        if s in (DOOR_OPEN, DOOR_VENTILATING):
            return False
        if s in (DOOR_OPENING, DOOR_CLOSING):
            return None
        return False

    @property
    def is_opening(self) -> bool:
        """Return True if the cover is opening."""
        return self._ctrl.door_state == DOOR_OPENING

    @property
    def is_closing(self) -> bool:
        """Return True if the cover is closing."""
        return self._ctrl.door_state == DOOR_CLOSING

    @property
    def current_cover_position(self) -> int:
        """Return current position with live estimation during movement."""
        return self._ctrl.get_live_position()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes including restore data."""
        c = self._ctrl
        return {
            "door_state_detail": c.door_state,
            "is_ventilating": c.is_ventilating,
            "is_pulsing": c.is_pulsing,
            "actor_reachable": c.actor_reachable,
            "sync_state": c._sync_state,
            "pulse_count": c._pulse_count,
            "_restore_data": json.dumps(c.get_restore_data()),
        }

    # Phase 2.2: Action exceptions
    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the garage door."""
        try:
            await self._ctrl.async_open()
        except Exception as err:
            raise HomeAssistantError(f"Failed to open garage door: {err}") from err

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the garage door."""
        try:
            await self._ctrl.async_close()
        except Exception as err:
            raise HomeAssistantError(f"Failed to close garage door: {err}") from err

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the garage door."""
        try:
            await self._ctrl.async_stop()
        except Exception as err:
            raise HomeAssistantError(f"Failed to stop garage door: {err}") from err

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Set cover to a target position."""
        target = kwargs.get("position", 0)
        try:
            if target == 0:
                await self._ctrl.async_close()
            elif target == 100:
                await self._ctrl.async_open()
            elif target <= 15 and self._ctrl.door_state == DOOR_CLOSED:
                await self._ctrl.async_open_ventilation()
            else:
                await self._ctrl.async_open()
        except Exception as err:
            raise HomeAssistantError(f"Failed to set position to {target}: {err}") from err
