"""Switch platform – ventilation auto, rain auto close, manual ventilation."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from .const import DOMAIN
from .controller import SmartGarageController

async def async_setup_entry(hass, entry, async_add_entities):
    ctrl = hass.data[DOMAIN][entry.entry_id]
    entities = []
    if ctrl.vent_enabled_cfg:
        entities.append(VentAutoSwitch(entry, ctrl))
        entities.append(ManualVentSwitch(entry, ctrl))
    if ctrl.rain_configured:
        entities.append(RainAutoSwitch(entry, ctrl))
    if entities:
        async_add_entities(entities, True)

class _Base(RestoreEntity, SwitchEntity):
    _attr_has_entity_name = True
    _ctrl: SmartGarageController
    @property
    def device_info(self): return self._ctrl.device_info

class VentAutoSwitch(_Base):
    _attr_icon = "mdi:fan-auto"
    _attr_translation_key = "ventilation_auto"
    def __init__(self,e,c): self._ctrl=c; self._attr_unique_id=f"{DOMAIN}_{e.entry_id}_sw_vent"; self._is_on=False
    @property
    def is_on(self): return self._is_on
    async def async_added_to_hass(self):
        last=await self.async_get_last_state()
        if last and last.state=="on": self._is_on=True
        self._ctrl.sw_ventilation_auto=self._is_on
    async def async_turn_on(self,**kw): self._is_on=True; self._ctrl.sw_ventilation_auto=True; self.async_write_ha_state()
    async def async_turn_off(self,**kw):
        self._is_on=False; self._ctrl.sw_ventilation_auto=False; self.async_write_ha_state()
        if self._ctrl.is_ventilating: await self._ctrl.async_close_ventilation()

class RainAutoSwitch(_Base):
    _attr_icon = "mdi:weather-pouring"
    _attr_translation_key = "rain_auto_close"
    def __init__(self,e,c): self._ctrl=c; self._attr_unique_id=f"{DOMAIN}_{e.entry_id}_sw_rain"; self._is_on=False
    @property
    def is_on(self): return self._is_on
    async def async_added_to_hass(self):
        last=await self.async_get_last_state()
        if last and last.state=="on": self._is_on=True
        self._ctrl.sw_rain_auto_close=self._is_on
    async def async_turn_on(self,**kw): self._is_on=True; self._ctrl.sw_rain_auto_close=True; self.async_write_ha_state()
    async def async_turn_off(self,**kw): self._is_on=False; self._ctrl.sw_rain_auto_close=False; self.async_write_ha_state()

class ManualVentSwitch(_Base):
    _attr_icon = "mdi:garage-open-variant"
    _attr_translation_key = "manual_ventilation"
    def __init__(self,e,c): self._ctrl=c; self._attr_unique_id=f"{DOMAIN}_{e.entry_id}_sw_manual_vent"; self._is_on=False
    @property
    def is_on(self): return self._ctrl.is_ventilating
    async def async_added_to_hass(self):
        last=await self.async_get_last_state()
        self._ctrl.register_update_callback(self._u)
    async def async_will_remove_from_hass(self): self._ctrl.unregister_update_callback(self._u)
    def _u(self): self.async_write_ha_state()
    async def async_turn_on(self,**kw):
        self._ctrl.sw_manual_ventilation=True
        await self._ctrl.async_set_manual_ventilation(True)
        self.async_write_ha_state()
    async def async_turn_off(self,**kw):
        self._ctrl.sw_manual_ventilation=False
        await self._ctrl.async_set_manual_ventilation(False)
        self.async_write_ha_state()
