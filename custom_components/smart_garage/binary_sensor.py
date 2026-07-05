"""Binary sensor platform."""
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import callback
from .const import DOMAIN
from .controller import SmartGarageController

async def async_setup_entry(hass, entry, async_add_entities):
    ctrl = hass.data[DOMAIN][entry.entry_id]
    e = [ActorReachable(entry, ctrl)]
    if ctrl.vent_enabled_cfg: e.append(VentActive(entry, ctrl))
    async_add_entities(e, True)

class _B(BinarySensorEntity):
    _attr_has_entity_name=True; _ctrl: SmartGarageController
    @property
    def device_info(self): return self._ctrl.device_info
    async def async_added_to_hass(self): self._ctrl.register_update_callback(self._u)
    async def async_will_remove_from_hass(self): self._ctrl.unregister_update_callback(self._u)
    @callback
    def _u(self): self.async_write_ha_state()

class VentActive(_B):
    _attr_device_class=BinarySensorDeviceClass.OPENING; _attr_icon="mdi:air-filter"
    _attr_translation_key="ventilation_active"
    def __init__(self,e,c): self._ctrl=c; self._attr_unique_id=f"{DOMAIN}_{e.entry_id}_vent_active"
    @property
    def is_on(self): return self._ctrl.is_ventilating

class ActorReachable(_B):
    _attr_device_class=BinarySensorDeviceClass.CONNECTIVITY; _attr_icon="mdi:lan-connect"
    _attr_translation_key="actor_reachable"
    def __init__(self,e,c): self._ctrl=c; self._attr_unique_id=f"{DOMAIN}_{e.entry_id}_actor_reachable"
    @property
    def is_on(self): return self._ctrl.actor_reachable
