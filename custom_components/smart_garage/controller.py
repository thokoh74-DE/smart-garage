"""Central controller for Smart Garage v1.0 – pulse-counting state machine."""
from __future__ import annotations
import asyncio, logging, math
from datetime import datetime, timedelta
from typing import Any
from homeassistant.const import STATE_ON, STATE_OFF, STATE_UNAVAILABLE, STATE_UNKNOWN, STATE_HOME
from homeassistant.core import HomeAssistant, callback, Event
from homeassistant.helpers.event import async_track_state_change_event, async_track_time_interval, async_call_later
from homeassistant.helpers.sun import is_up as sun_is_up
from homeassistant.util import dt as dt_util
from .const import *

_LOGGER = logging.getLogger(__name__)
_CYCLE_FROM_CLOSED = [DOOR_OPENING, DOOR_STOPPED_UP, DOOR_CLOSING, DOOR_STOPPED_DOWN]
_CYCLE_FROM_OPEN = [DOOR_CLOSING, DOOR_STOPPED_DOWN, DOOR_OPENING, DOOR_STOPPED_UP]

def absolute_humidity(temp_c: float, rel_hum: float) -> float | None:
    if not (0 <= rel_hum <= 100): return None
    try:
        es = 6.112 * math.exp((17.67 * temp_c) / (temp_c + 243.5))
        return round((es * rel_hum * 2.1674) / (273.15 + temp_c), 2)
    except (ValueError, ZeroDivisionError, OverflowError): return None

def dew_point(temp_c: float, rel_hum: float) -> float | None:
    if not (0 < rel_hum <= 100): return None
    try:
        a = (17.67 * temp_c) / (243.5 + temp_c) + math.log(rel_hum / 100)
        return round((243.5 * a) / (17.67 - a), 1)
    except (ValueError, ZeroDivisionError, OverflowError): return None

def _safe_float(hass, eid):
    s = hass.states.get(eid)
    if s is None or s.state in (STATE_UNAVAILABLE, STATE_UNKNOWN): return None
    try: return float(s.state)
    except (ValueError, TypeError): return None

class SmartGarageController:
    def __init__(self, hass: HomeAssistant, entry_id: str, config: dict[str, Any]):
        self.hass = hass
        self.entry_id = entry_id
        self._config = config

        self.control_switch: str = config[CONF_CONTROL_SWITCH]
        self.pulse_ms = int(config.get(CONF_PULSE_DURATION_MS, DEFAULT_PULSE_DURATION_MS))
        self.pulse_delay = float(config.get(CONF_PULSE_DELAY_S, DEFAULT_PULSE_DELAY_S))
        self.travel_time = int(config.get(CONF_TRAVEL_TIME_S, DEFAULT_TRAVEL_TIME_S))
        self.vent_open_s = float(config.get(CONF_VENTILATION_OPEN_S, DEFAULT_VENTILATION_OPEN_S))

        self.closed_sensor: str | None = config.get(CONF_CLOSED_SENSOR)
        self.open_sensor: str | None = config.get(CONF_OPEN_SENSOR)
        self.closed_invert: bool = config.get(CONF_CLOSED_SENSOR_INVERT, False)
        self.open_invert: bool = config.get(CONF_OPEN_SENSOR_INVERT, False)
        self.vibration_sensor: str | None = config.get(CONF_VIBRATION_SENSOR)
        self.external_button: str | None = config.get(CONF_EXTERNAL_BUTTON)

        self.safety_enabled: bool = config.get(CONF_SAFETY_ENABLED, False)
        self.safety_vibration_s = int(config.get(CONF_SAFETY_VIBRATION_S, DEFAULT_SAFETY_VIBRATION_S))
        self.safety_close_delay = int(config.get(CONF_SAFETY_CLOSE_DELAY_S, DEFAULT_SAFETY_CLOSE_DELAY_S))
        self.notify_service: str = config.get(CONF_NOTIFY_SERVICE, "")

        self.vent_enabled_cfg: bool = config.get(CONF_ENABLE_VENTILATION, False)
        self.indoor_temp_id: str | None = config.get(CONF_INDOOR_TEMP_SENSOR)
        self.indoor_hum_id: str | None = config.get(CONF_INDOOR_HUMIDITY_SENSOR)
        self.outdoor_temp_id: str | None = config.get(CONF_OUTDOOR_TEMP_SENSOR)
        self.outdoor_hum_id: str | None = config.get(CONF_OUTDOOR_HUMIDITY_SENSOR)
        self.rain_sensor_id: str | None = config.get(CONF_RAIN_SENSOR)
        self.hum_threshold = float(config.get(CONF_HUMIDITY_THRESHOLD, DEFAULT_HUMIDITY_THRESHOLD))
        self.ah_diff_threshold = float(config.get(CONF_AH_DIFF_THRESHOLD, DEFAULT_AH_DIFF_THRESHOLD))
        self.check_interval = int(config.get(CONF_VENTILATION_CHECK_INTERVAL, DEFAULT_VENTILATION_CHECK_INTERVAL))
        self.presence_entity: str | None = config.get(CONF_PRESENCE_ENTITY)
        self.rain_close_delay = int(config.get(CONF_RAIN_CLOSE_DELAY_MIN, DEFAULT_RAIN_CLOSE_DELAY_MIN))

        # Check if humidity sensors are fully configured
        self.humidity_configured = all([self.indoor_temp_id, self.indoor_hum_id,
                                        self.outdoor_temp_id, self.outdoor_hum_id])
        self.rain_configured = bool(self.rain_sensor_id)

        # Pulse-counting state machine
        self._sync_state: str = DOOR_CLOSED
        self._pulse_count: int = 0
        self.position: int = 0
        self.is_ventilating: bool = False
        self.last_command: str = ""
        self.last_drive: str = DOOR_CLOSED

        self.is_pulsing: bool = False
        self._pulse_lock = asyncio.Lock()
        self._last_pulse_time: datetime | None = None
        self._move_start: datetime | None = None
        self._last_opened_at: datetime | None = None
        self._safety_pending: bool = False
        self._command_seq: int = 0

        # Ventilation
        self.ah_indoor: float | None = None
        self.ah_outdoor: float | None = None
        self.ah_diff: float | None = None
        self.dp_indoor: float | None = None
        self.dp_outdoor: float | None = None
        self.is_raining: bool = False
        self.vent_recommendation: str = VENT_NOT_RECOMMEND

        # Switch states (set by switch entities via RestoreEntity)
        self.sw_ventilation_auto: bool = False
        self.sw_rain_auto_close: bool = False
        self.sw_manual_ventilation: bool = False

        self.actor_reachable: bool = True
        self._unsub: list = []
        self._travel_unsub = None
        self._rain_close_unsub = None
        self._safety_close_unsub = None
        self._update_callbacks: list = []

    # ── Device info ───────────────────────────────────────────────
    @property
    def device_info(self):
        from homeassistant.helpers.entity import DeviceInfo
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry_id)},
            name=self._config.get(CONF_NAME, "Smart Garage"),
            manufacturer="Smart Garage",
            model="Impulse Garage Door v1",
            sw_version="1.0.0",
        )

    # ── Derived door state ────────────────────────────────────────
    @property
    def door_state(self) -> str:
        if self._pulse_count == 0:
            return self._sync_state
        cycle = _CYCLE_FROM_CLOSED if self._sync_state == DOOR_CLOSED else _CYCLE_FROM_OPEN
        return cycle[(self._pulse_count - 1) % 4]

    # ── State persistence ─────────────────────────────────────────
    def get_restore_data(self) -> dict[str, Any]:
        return {"sync_state": self._sync_state, "pulse_count": self._pulse_count,
                "position": self.position, "is_ventilating": self.is_ventilating,
                "last_command": self.last_command, "last_drive": self.last_drive}

    def restore_state(self, data: dict[str, Any]) -> None:
        if not data: return
        self._sync_state = data.get("sync_state", DOOR_CLOSED)
        self._pulse_count = data.get("pulse_count", 0)
        self.position = data.get("position", 0)
        self.is_ventilating = data.get("is_ventilating", False)
        self.last_command = data.get("last_command", "")
        self.last_drive = data.get("last_drive", DOOR_CLOSED)
        _LOGGER.info("Smart Garage: Restored sync=%s pulses=%d pos=%d", self._sync_state, self._pulse_count, self.position)

    # ── Callbacks ─────────────────────────────────────────────────
    def register_update_callback(self, cb): self._update_callbacks.append(cb)
    def unregister_update_callback(self, cb):
        if cb in self._update_callbacks: self._update_callbacks.remove(cb)
    def _notify_update(self):
        self.last_drive = self.door_state
        for cb in self._update_callbacks: cb()

    # ── Lifecycle ─────────────────────────────────────────────────
    async def async_start(self):
        tracked = [self.control_switch]
        for s in [self.closed_sensor, self.open_sensor, self.vibration_sensor, self.rain_sensor_id]:
            if s: tracked.append(s)
        vent_sensors = []
        if self.vent_enabled_cfg and self.humidity_configured:
            for s in [self.indoor_temp_id, self.indoor_hum_id, self.outdoor_temp_id, self.outdoor_hum_id]:
                if s: vent_sensors.append(s)
        self._unsub.append(async_track_state_change_event(self.hass, tracked + vent_sensors, self._async_state_changed))
        if self.external_button:
            self._unsub.append(async_track_state_change_event(self.hass, [self.external_button], self._async_external_button))
        if self.vent_enabled_cfg and self.humidity_configured:
            self._unsub.append(async_track_time_interval(self.hass, self._async_periodic_vent_check, timedelta(minutes=self.check_interval)))
        self._sync_from_sensors()
        if self.vent_enabled_cfg and self.humidity_configured:
            self._evaluate_ventilation()

    async def async_stop(self):
        for u in self._unsub: u()
        self._unsub.clear()
        for h in [self._travel_unsub, self._rain_close_unsub, self._safety_close_unsub]:
            if h: h()
        self._travel_unsub = self._rain_close_unsub = self._safety_close_unsub = None

    # ── Sensor helpers ────────────────────────────────────────────
    def _sensor_active(self, eid, invert):
        s = self.hass.states.get(eid)
        if s is None or s.state in (STATE_UNAVAILABLE, STATE_UNKNOWN): return False
        is_on = s.state == STATE_ON
        return (not is_on) if invert else is_on

    def _sync_from_sensors(self):
        closed = self.closed_sensor and self._sensor_active(self.closed_sensor, self.closed_invert)
        opened = self.open_sensor and self._sensor_active(self.open_sensor, self.open_invert)
        if closed and not opened: self._do_sync(DOOR_CLOSED, 0)
        elif opened and not closed: self._do_sync(DOOR_OPEN, 100)
        elif closed and opened:
            _LOGGER.warning("Smart Garage: Both sensors active – defaulting to CLOSED")
            self._do_sync(DOOR_CLOSED, 0)

    def _do_sync(self, state, position):
        old = self.door_state
        self._sync_state = state
        self._pulse_count = 0
        self.position = position
        self._move_start = None
        if state == DOOR_CLOSED:
            self.is_ventilating = False
            self._safety_pending = False
        self.last_drive = state
        _LOGGER.info("Smart Garage: SYNC %s → %s (pos=%d)", old, state, position)

    # ── Pulse counting ────────────────────────────────────────────
    def _advance_pulse(self):
        self._pulse_count += 1
        new = self.door_state
        _LOGGER.debug("Smart Garage: Pulse #%d sync=%s → %s", self._pulse_count, self._sync_state, new)
        if new in (DOOR_OPENING, DOOR_CLOSING):
            self._move_start = dt_util.utcnow()
        else:
            self._estimate_position()
            self._move_start = None
        if new in (DOOR_OPENING, DOOR_OPEN):
            self._last_opened_at = dt_util.utcnow()
        self.last_drive = new
        return new

    def _estimate_position(self):
        if self._move_start is None: return
        elapsed = (dt_util.utcnow() - self._move_start).total_seconds()
        frac = min(elapsed / self.travel_time, 1.0)
        state = self.door_state
        if state in (DOOR_OPENING, DOOR_STOPPED_UP, DOOR_VENTILATING):
            self.position = max(int(frac * 100), 1)
        elif state in (DOOR_CLOSING, DOOR_STOPPED_DOWN):
            self.position = max(int((1.0 - frac) * 100), 1)

    def get_live_position(self) -> int:
        """Calculate dynamic position during movement."""
        if self.door_state in (DOOR_OPENING, DOOR_CLOSING) and self._move_start:
            elapsed = (dt_util.utcnow() - self._move_start).total_seconds()
            frac = min(elapsed / self.travel_time, 1.0)
            if self.door_state == DOOR_OPENING:
                return max(int(frac * 100), 1)
            else:
                return max(int((1.0 - frac) * 100), 0)
        return self.position

    # ── Pulse control ─────────────────────────────────────────────
    async def _pulse_once(self):
        domain = self.control_switch.split(".")[0]
        try:
            if domain == "button":
                await self.hass.services.async_call("button", "press", {"entity_id": self.control_switch})
            else:
                await self.hass.services.async_call("switch", "turn_on", {"entity_id": self.control_switch})
                await asyncio.sleep(self.pulse_ms / 1000)
                await self.hass.services.async_call("switch", "turn_off", {"entity_id": self.control_switch})
            self._last_pulse_time = dt_util.utcnow()
            return True
        except Exception:
            _LOGGER.exception("Smart Garage: Pulse failed")
            return False

    async def _do_pulse(self):
        async with self._pulse_lock:
            self.is_pulsing = True
            ok = await self._pulse_once()
            if ok:
                self._advance_pulse()
                self._notify_update()
            self.is_pulsing = False
            return ok

    async def _multi_pulse(self, count):
        seq = self._command_seq
        for i in range(count):
            if self._command_seq != seq:
                _LOGGER.info("Smart Garage: Multi-pulse aborted at %d/%d", i + 1, count)
                break
            ok = await self._do_pulse()
            if not ok: break
            if i < count - 1: await asyncio.sleep(self.pulse_delay)

    def _start_travel_timer(self, target):
        if self._travel_unsub:
            self._travel_unsub()
            self._travel_unsub = None
        # If position sensor is configured, let the sensor handle definitive sync.
        # Travel timer is ONLY a fallback when no sensor is available.
        if target == DOOR_OPEN and self.open_sensor: return
        if target == DOOR_CLOSED and self.closed_sensor: return

        if target == DOOR_OPEN: remaining = (100 - self.position) / 100
        else: remaining = self.position / 100
        secs = max(remaining * self.travel_time, 1)

        @callback
        def _done(_now):
            self._travel_unsub = None
            if self.door_state == DOOR_OPENING: self._do_sync(DOOR_OPEN, 100)
            elif self.door_state == DOOR_CLOSING: self._do_sync(DOOR_CLOSED, 0)
            self._notify_update()
        self._travel_unsub = async_call_later(self.hass, secs, _done)

    def _cancel_travel_timer(self):
        if self._travel_unsub:
            self._travel_unsub()
            self._travel_unsub = None

    # ── Cover commands ────────────────────────────────────────────
    async def async_open(self):
        self._command_seq += 1
        state = self.door_state
        self.last_command = "up"
        if state in (DOOR_OPEN, DOOR_OPENING): return
        if state in (DOOR_CLOSED, DOOR_STOPPED_DOWN):
            await self._do_pulse()
            self._start_travel_timer(DOOR_OPEN)
        elif state == DOOR_CLOSING:
            await self._multi_pulse(2)
            self._start_travel_timer(DOOR_OPEN)
        elif state in (DOOR_STOPPED_UP, DOOR_VENTILATING):
            await self._multi_pulse(3)
            self._start_travel_timer(DOOR_OPEN)

    async def async_close(self):
        self._command_seq += 1
        state = self.door_state
        self.last_command = "down"
        if state in (DOOR_CLOSED, DOOR_CLOSING): return
        if state in (DOOR_OPEN, DOOR_STOPPED_UP, DOOR_VENTILATING):
            await self._do_pulse()
            self._start_travel_timer(DOOR_CLOSED)
        elif state == DOOR_STOPPED_DOWN:
            await self._multi_pulse(3)
            self._start_travel_timer(DOOR_CLOSED)
        elif state == DOOR_OPENING:
            await self._multi_pulse(2)
            self._start_travel_timer(DOOR_CLOSED)

    async def async_stop(self):
        self._command_seq += 1
        state = self.door_state
        self.last_command = "stop"
        if state in (DOOR_CLOSED, DOOR_OPEN, DOOR_STOPPED_UP, DOOR_STOPPED_DOWN, DOOR_VENTILATING):
            return
        await self._do_pulse()
        self._notify_update()
        self._cancel_travel_timer()

    async def async_open_ventilation(self):
        self._command_seq += 1
        if self.door_state != DOOR_CLOSED: return
        self.last_command = "ventilate"
        _LOGGER.info("Smart Garage: Ventilation open (%.1fs)", self.vent_open_s)
        await self._do_pulse()
        await asyncio.sleep(self.vent_open_s)
        await self._do_pulse()
        self.is_ventilating = True
        self._notify_update()

    async def async_close_ventilation(self):
        self._command_seq += 1
        state = self.door_state
        if state not in (DOOR_STOPPED_UP, DOOR_VENTILATING):
            if state in (DOOR_OPEN, DOOR_OPENING): await self.async_close()
            return
        self.last_command = "ventilate_close"
        await self._do_pulse()
        self.is_ventilating = False
        self._start_travel_timer(DOOR_CLOSED)

    # ── Manual ventilation toggle ─────────────────────────────────
    async def async_set_manual_ventilation(self, on: bool):
        if on:
            if self.door_state == DOOR_CLOSED:
                await self.async_open_ventilation()
        else:
            if self.is_ventilating:
                await self.async_close_ventilation()
            self.sw_manual_ventilation = False

    # ── Sensor event handling ─────────────────────────────────────
    @callback
    def _async_state_changed(self, event: Event):
        eid = event.data.get("entity_id")
        new = event.data.get("new_state")
        old = event.data.get("old_state")
        if new is None: return

        if eid == self.control_switch:
            prev = self.actor_reachable
            self.actor_reachable = new.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN)
            if prev and not self.actor_reachable and self.door_state != DOOR_CLOSED:
                self._fire_notification("Actor unreachable", "Garage door is open and actor is unreachable.", critical=True)
            if new.state == STATE_ON and old and old.state != STATE_ON and not self.is_pulsing:
                if self._last_pulse_time and (dt_util.utcnow() - self._last_pulse_time).total_seconds() < 2.0:
                    self._notify_update(); return
                _LOGGER.info("Smart Garage: External switch activation")
                self._advance_pulse()
            self._notify_update(); return

        if eid == self.closed_sensor:
            if new.state in (STATE_UNAVAILABLE, STATE_UNKNOWN): return
            if self._sensor_active(eid, self.closed_invert):
                self._do_sync(DOOR_CLOSED, 0)
                self._cancel_travel_timer()
                self._notify_update()

        elif eid == self.open_sensor:
            if new.state in (STATE_UNAVAILABLE, STATE_UNKNOWN): return
            if self._sensor_active(eid, self.open_invert):
                if self.is_ventilating and self.safety_enabled:
                    self._trigger_accidental_open_safety()
                else:
                    self._do_sync(DOOR_OPEN, 100)
                    self._cancel_travel_timer()
                self._notify_update()

        elif eid == self.vibration_sensor:
            is_on = new.state == STATE_ON
            was_on = old and old.state == STATE_ON
            if is_on and not was_on and self.is_ventilating and self.safety_enabled:
                self._schedule_vibration_safety()
            if not is_on and was_on:
                if self.closed_sensor and self._sensor_active(self.closed_sensor, self.closed_invert):
                    self._do_sync(DOOR_CLOSED, 0)
                elif self.open_sensor and self._sensor_active(self.open_sensor, self.open_invert):
                    if not (self.is_ventilating and self.safety_enabled):
                        self._do_sync(DOOR_OPEN, 100)
                else:
                    self._estimate_position()
                self._notify_update()

        elif eid == self.rain_sensor_id:
            was = self.is_raining
            self.is_raining = new.state == STATE_ON
            if self.is_raining and not was: self._handle_rain_start()
            if self.humidity_configured: self._evaluate_ventilation()
            self._notify_update()

        elif eid in (self.indoor_temp_id, self.indoor_hum_id, self.outdoor_temp_id, self.outdoor_hum_id):
            self._evaluate_ventilation()
            self._notify_update()

    @callback
    def _async_external_button(self, event: Event):
        new = event.data.get("new_state")
        if new is None or self.is_pulsing: return
        if self._last_pulse_time and (dt_util.utcnow() - self._last_pulse_time).total_seconds() < 3.0: return
        _LOGGER.info("Smart Garage: External button press")
        self.last_command = "manual"
        self._advance_pulse()
        ds = self.door_state
        if ds == DOOR_OPENING: self._start_travel_timer(DOOR_OPEN)
        elif ds == DOOR_CLOSING: self._start_travel_timer(DOOR_CLOSED)
        if self.is_ventilating: self.is_ventilating = False
        self._notify_update()

    # ── Safety ────────────────────────────────────────────────────
    def _schedule_vibration_safety(self):
        if self._safety_close_unsub: self._safety_close_unsub()
        @callback
        def _check(_now):
            self._safety_close_unsub = None
            if not self.is_ventilating: return
            if self.vibration_sensor:
                vs = self.hass.states.get(self.vibration_sensor)
                if vs and vs.state == STATE_ON: self._trigger_accidental_open_safety()
        self._safety_close_unsub = async_call_later(self.hass, self.safety_vibration_s, _check)

    def _trigger_accidental_open_safety(self):
        if self._safety_pending: return
        self._safety_pending = True
        self._fire_notification("Accidental opening", f"Door will close in {self.safety_close_delay}s.", critical=True)
        @callback
        def _close(_now):
            if self.door_state not in (DOOR_CLOSED, DOOR_CLOSING):
                self.hass.async_create_task(self.async_close())
            self._safety_pending = False
        async_call_later(self.hass, self.safety_close_delay, _close)

    # ── Rain ──────────────────────────────────────────────────────
    def _handle_rain_start(self):
        if not self.sw_rain_auto_close or not self.rain_configured: return
        if self.door_state == DOOR_CLOSED: return
        if self.is_ventilating:
            self._fire_notification("Rain – closing ventilation", "Rain detected, closing garage door.")
            self.hass.async_create_task(self.async_close_ventilation())
            return
        if self._last_opened_at is None: return
        elapsed = (dt_util.utcnow() - self._last_opened_at).total_seconds()
        req = self.rain_close_delay * 60
        if elapsed >= req:
            self._fire_notification("Rain – closing door", "Rain detected, closing garage door now.")
            self.hass.async_create_task(self.async_close())
        else:
            rem = req - elapsed
            self._fire_notification("Rain – door open", f"Rain detected. Door will close in {int(rem)}s if still raining.")
            if self._rain_close_unsub: self._rain_close_unsub()
            @callback
            def _delayed(_now):
                self._rain_close_unsub = None
                if not self.is_raining or self.door_state == DOOR_CLOSED or not self.sw_rain_auto_close: return
                self._fire_notification("Rain – closing now", "Still raining. Closing garage door.")
                self.hass.async_create_task(self.async_close())
            self._rain_close_unsub = async_call_later(self.hass, rem, _delayed)

    # ── Ventilation ───────────────────────────────────────────────
    def _evaluate_ventilation(self):
        if not self.vent_enabled_cfg or not self.humidity_configured:
            self.vent_recommendation = VENT_NOT_RECOMMEND; return
        it = _safe_float(self.hass, self.indoor_temp_id)
        ih = _safe_float(self.hass, self.indoor_hum_id)
        ot = _safe_float(self.hass, self.outdoor_temp_id)
        oh = _safe_float(self.hass, self.outdoor_hum_id)
        if self.rain_configured:
            rs = self.hass.states.get(self.rain_sensor_id)
            self.is_raining = rs is not None and rs.state == STATE_ON
        self.ah_indoor = absolute_humidity(it, ih) if it is not None and ih is not None else None
        self.dp_indoor = dew_point(it, ih) if it is not None and ih is not None else None
        self.ah_outdoor = absolute_humidity(ot, oh) if ot is not None and oh is not None else None
        self.dp_outdoor = dew_point(ot, oh) if ot is not None and oh is not None else None
        self.ah_diff = round(self.ah_indoor - self.ah_outdoor, 2) if self.ah_indoor is not None and self.ah_outdoor is not None else None
        if any(v is None for v in (self.ah_indoor, self.ah_outdoor, ih)) or self.is_raining:
            self.vent_recommendation = VENT_NOT_RECOMMEND; return
        if self.ah_outdoor >= self.ah_indoor:
            self.vent_recommendation = VENT_NOT_RECOMMEND; return
        if self.ah_diff >= self.ah_diff_threshold and ih >= self.hum_threshold:
            self.vent_recommendation = VENT_RECOMMEND
        elif self.ah_diff >= (self.ah_diff_threshold * 0.5):
            self.vent_recommendation = VENT_NEUTRAL
        else:
            self.vent_recommendation = VENT_NOT_RECOMMEND

    @callback
    def _async_periodic_vent_check(self, _now):
        self._evaluate_ventilation()
        self._notify_update()
        if not self.sw_ventilation_auto: return
        if self.presence_entity:
            ps = self.hass.states.get(self.presence_entity)
            if ps and ps.state not in (STATE_HOME, "home", "Anwesend"):
                if self.is_ventilating: self.hass.async_create_task(self.async_close_ventilation())
                return
        if not sun_is_up(self.hass):
            if self.is_ventilating: self.hass.async_create_task(self.async_close_ventilation())
            return
        if self.vent_recommendation == VENT_RECOMMEND and not self.is_ventilating and self.door_state == DOOR_CLOSED:
            self.hass.async_create_task(self.async_open_ventilation())
        elif self.vent_recommendation == VENT_NOT_RECOMMEND and self.is_ventilating:
            self.hass.async_create_task(self.async_close_ventilation())

    # ── Notifications ─────────────────────────────────────────────
    def _fire_notification(self, title, message, critical=False):
        _LOGGER.info("Smart Garage: %s – %s", title, message)
        self.hass.bus.async_fire(EVENT_NOTIFICATION, {"title": title, "message": message, "critical": critical})
        if self.notify_service:
            parts = self.notify_service.split(".", 1)
            if len(parts) == 2:
                self.hass.async_create_task(self.hass.services.async_call(parts[0], parts[1], {"title": title, "message": message}))
        else:
            self.hass.async_create_task(self.hass.services.async_call("persistent_notification", "create", {"title": title, "message": message}))
