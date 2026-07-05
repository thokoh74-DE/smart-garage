"""Cover platform with state persistence."""
from __future__ import annotations
import json
from typing import Any
from homeassistant.components.cover import CoverDeviceClass, CoverEntity, CoverEntityFeature
from homeassistant.core import callback
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN, CONF_NAME, DOOR_CLOSED, DOOR_OPENING, DOOR_CLOSING, DOOR_OPEN, DOOR_VENTILATING
from .controller import SmartGarageController

async def async_setup_entry(hass, entry, async_add_entities):
    ctrl = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SmartGarageCover(entry, ctrl)], True)

class SmartGarageCover(RestoreEntity, CoverEntity):
    _attr_device_class = CoverDeviceClass.GARAGE
    _attr_has_entity_name = True

    def __init__(self, entry, ctrl):
        self._ctrl = ctrl
        self._attr_unique_id = f"{DOMAIN}_{entry.entry_id}_cover"
        self._attr_name = None

    @property
    def device_info(self): return self._ctrl.device_info

    async def async_added_to_hass(self):
        last = await self.async_get_last_state()
        if last and last.attributes:
            rd = last.attributes.get("_restore_data")
            if rd:
                try: self._ctrl.restore_state(json.loads(rd) if isinstance(rd, str) else rd)
                except: pass
        self._ctrl.register_update_callback(self._upd)

    async def async_will_remove_from_hass(self):
        self._ctrl.unregister_update_callback(self._upd)

    @callback
    def _upd(self): self.async_write_ha_state()

    @property
    def supported_features(self):
        return CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP | CoverEntityFeature.SET_POSITION

    @property
    def is_closed(self):
        s = self._ctrl.door_state
        if s == DOOR_CLOSED: return True
        if s in (DOOR_OPEN, DOOR_VENTILATING): return False
        if s in (DOOR_OPENING, DOOR_CLOSING): return None
        return False

    @property
    def is_opening(self): return self._ctrl.door_state == DOOR_OPENING
    @property
    def is_closing(self): return self._ctrl.door_state == DOOR_CLOSING
    @property
    def current_cover_position(self): return self._ctrl.get_live_position()

    @property
    def extra_state_attributes(self):
        c = self._ctrl
        return {"door_state_detail": c.door_state, "is_ventilating": c.is_ventilating,
                "is_pulsing": c.is_pulsing, "actor_reachable": c.actor_reachable,
                "sync_state": c._sync_state, "pulse_count": c._pulse_count,
                "_restore_data": json.dumps(c.get_restore_data())}

    async def async_open_cover(self, **kw): await self._ctrl.async_open()
    async def async_close_cover(self, **kw): await self._ctrl.async_close()
    async def async_stop_cover(self, **kw): await self._ctrl.async_stop()
    async def async_set_cover_position(self, **kw):
        t = kw.get("position", 0)
        if t == 0: await self._ctrl.async_close()
        elif t == 100: await self._ctrl.async_open()
        elif t <= 15 and self._ctrl.door_state == DOOR_CLOSED: await self._ctrl.async_open_ventilation()
        else: await self._ctrl.async_open()
