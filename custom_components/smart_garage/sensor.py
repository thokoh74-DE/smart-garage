"""Sensor platform – ventilation + diagnostics, all names via translation_key."""
from __future__ import annotations
from typing import Any
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfTemperature
from homeassistant.core import callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.event import async_track_state_change_event
from .const import *
from .controller import SmartGarageController

LAST_DRIVE_OPTIONS = ["closed","opening","open","closing","stopped_up","stopped_down","ventilating"]
LAST_COMMAND_OPTIONS = ["up","down","stop","ventilate","ventilate_close","manual","none"]
_STATE_LABELS = {
    "de": {DOOR_CLOSED:"Geschlossen",DOOR_OPENING:"Wird geöffnet",DOOR_OPEN:"Geöffnet",DOOR_CLOSING:"Wird geschlossen",DOOR_VENTILATING:"Belüftung"},
    "en": {DOOR_CLOSED:"Closed",DOOR_OPENING:"Opening",DOOR_OPEN:"Opened",DOOR_CLOSING:"Closing",DOOR_VENTILATING:"Ventilating"},
}

async def async_setup_entry(hass, entry, async_add_entities):
    ctrl = hass.data[DOMAIN][entry.entry_id]
    e = [DiagLastDrive(entry,ctrl), DiagLastCommand(entry,ctrl), DiagCurrentState(entry,ctrl)]
    if ctrl.closed_sensor: e.append(DiagMirror(entry,hass,ctrl,"limit_switch_bottom",ctrl.closed_sensor,"endschalter_unten","mdi:arrow-collapse-down"))
    if ctrl.open_sensor: e.append(DiagMirror(entry,hass,ctrl,"limit_switch_top",ctrl.open_sensor,"endschalter_oben","mdi:arrow-collapse-up"))
    if ctrl.vibration_sensor: e.append(DiagMirror(entry,hass,ctrl,"vibration_sensor",ctrl.vibration_sensor,"vibration","mdi:vibrate"))
    e.append(DiagMirror(entry,hass,ctrl,"control_switch_mirror",ctrl.control_switch,"schaltaktor","mdi:electric-switch"))
    if ctrl.vent_enabled_cfg and ctrl.humidity_configured:
        e.extend([VentRec(entry,ctrl), AbsHum(entry,ctrl,"indoor"), AbsHum(entry,ctrl,"outdoor"), DewPt(entry,ctrl,"indoor"), DewPt(entry,ctrl,"outdoor")])
    async_add_entities(e, True)

class _CM:
    _ctrl: SmartGarageController
    @property
    def device_info(self): return self._ctrl.device_info
    async def async_added_to_hass(self): self._ctrl.register_update_callback(self._u)
    async def async_will_remove_from_hass(self): self._ctrl.unregister_update_callback(self._u)
    @callback
    def _u(self): self.async_write_ha_state()

class DiagLastDrive(_CM, SensorEntity):
    _attr_has_entity_name=True; _attr_entity_category=EntityCategory.DIAGNOSTIC; _attr_icon="mdi:page-last"
    _attr_device_class=SensorDeviceClass.ENUM; _attr_options=LAST_DRIVE_OPTIONS; _attr_translation_key="last_drive"
    def __init__(self,e,c): self._ctrl=c; self._attr_unique_id=f"{DOMAIN}_{e.entry_id}_last_drive"
    @property
    def native_value(self): return self._ctrl.last_drive

class DiagLastCommand(_CM, SensorEntity):
    _attr_has_entity_name=True; _attr_entity_category=EntityCategory.DIAGNOSTIC; _attr_icon="mdi:garage-alert"
    _attr_device_class=SensorDeviceClass.ENUM; _attr_options=LAST_COMMAND_OPTIONS; _attr_translation_key="last_command"
    def __init__(self,e,c): self._ctrl=c; self._attr_unique_id=f"{DOMAIN}_{e.entry_id}_last_cmd"
    @property
    def native_value(self): return self._ctrl.last_command or "none"

class DiagCurrentState(_CM, SensorEntity):
    _attr_has_entity_name=True; _attr_entity_category=EntityCategory.DIAGNOSTIC; _attr_icon="mdi:garage-variant"
    _attr_translation_key="current_state"
    def __init__(self,e,c): self._ctrl=c; self._attr_unique_id=f"{DOMAIN}_{e.entry_id}_current_state"
    @property
    def native_value(self):
        s,p = self._ctrl.door_state, self._ctrl.get_live_position()
        lang = "de" if self.hass and hasattr(self.hass.config,"language") and self.hass.config.language.startswith("de") else "en"
        if s in _STATE_LABELS.get(lang,_STATE_LABELS["en"]): return _STATE_LABELS[lang][s]
        if s in (DOOR_STOPPED_UP,DOOR_STOPPED_DOWN): return f"Position {p}%"
        return s
    @property
    def extra_state_attributes(self):
        return {"door_state_raw":self._ctrl.door_state,"position_pct":self._ctrl.get_live_position(),
                "sync_state":self._ctrl._sync_state,"pulse_count":self._ctrl._pulse_count}

class DiagMirror(SensorEntity):
    _attr_has_entity_name=True; _attr_entity_category=EntityCategory.DIAGNOSTIC
    def __init__(self,entry,hass,ctrl,tk,src,tag,icon):
        self._src=src; self._h=hass; self._ctrl=ctrl; self._unsub=None
        self._attr_unique_id=f"{DOMAIN}_{entry.entry_id}_{tag}"; self._attr_icon=icon; self._attr_translation_key=tk
    @property
    def device_info(self): return self._ctrl.device_info
    @property
    def native_value(self):
        s=self._h.states.get(self._src); return s.state if s else None
    @property
    def extra_state_attributes(self):
        s=self._h.states.get(self._src)
        return {"source_entity":self._src,"last_changed":str(s.last_changed)} if s else {}
    async def async_added_to_hass(self):
        self._unsub = async_track_state_change_event(self.hass,[self._src],self._c)
    async def async_will_remove_from_hass(self):
        if self._unsub: self._unsub()
    @callback
    def _c(self,ev): self.async_write_ha_state()

class VentRec(_CM, SensorEntity):
    _attr_has_entity_name=True; _attr_icon="mdi:air-filter"
    _attr_device_class=SensorDeviceClass.ENUM; _attr_options=["recommend","neutral","not_recommend"]
    _attr_translation_key="ventilation_recommendation"
    def __init__(self,e,c): self._ctrl=c; self._attr_unique_id=f"{DOMAIN}_{e.entry_id}_vent_rec"
    @property
    def native_value(self): return self._ctrl.vent_recommendation
    @property
    def extra_state_attributes(self):
        c=self._ctrl
        return {"ah_indoor":c.ah_indoor,"ah_outdoor":c.ah_outdoor,"ah_diff":c.ah_diff,
                "dp_indoor":c.dp_indoor,"dp_outdoor":c.dp_outdoor,"is_raining":c.is_raining}

class AbsHum(_CM, SensorEntity):
    _attr_has_entity_name=True; _attr_state_class=SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement="g/m³"; _attr_icon="mdi:water"
    def __init__(self,e,c,loc):
        self._ctrl=c; self._loc=loc
        self._attr_unique_id=f"{DOMAIN}_{e.entry_id}_ah_{loc}"; self._attr_translation_key=f"abs_humidity_{loc}"
    @property
    def native_value(self): return self._ctrl.ah_indoor if self._loc=="indoor" else self._ctrl.ah_outdoor

class DewPt(_CM, SensorEntity):
    _attr_has_entity_name=True; _attr_device_class=SensorDeviceClass.TEMPERATURE
    _attr_state_class=SensorStateClass.MEASUREMENT; _attr_native_unit_of_measurement=UnitOfTemperature.CELSIUS
    _attr_icon="mdi:thermometer-water"
    def __init__(self,e,c,loc):
        self._ctrl=c; self._loc=loc
        self._attr_unique_id=f"{DOMAIN}_{e.entry_id}_dp_{loc}"; self._attr_translation_key=f"dew_point_{loc}"
    @property
    def native_value(self): return self._ctrl.dp_indoor if self._loc=="indoor" else self._ctrl.dp_outdoor
