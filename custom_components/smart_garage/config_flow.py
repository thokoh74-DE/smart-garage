"""Config flow with menu-based options for Smart Garage."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_AH_DIFF_THRESHOLD,
    CONF_CLOSED_SENSOR,
    CONF_CLOSED_SENSOR_INVERT,
    CONF_CONTROL_SWITCH,
    CONF_ENABLE_VENTILATION,
    CONF_EXTERNAL_BUTTON,
    CONF_HUMIDITY_THRESHOLD,
    CONF_INDOOR_HUMIDITY_SENSOR,
    CONF_INDOOR_TEMP_SENSOR,
    CONF_NAME,
    CONF_NOTIFY_SERVICE,
    CONF_OPEN_SENSOR,
    CONF_OPEN_SENSOR_INVERT,
    CONF_OUTDOOR_HUMIDITY_SENSOR,
    CONF_OUTDOOR_TEMP_SENSOR,
    CONF_PRESENCE_ENTITY,
    CONF_PULSE_DELAY_S,
    CONF_PULSE_DURATION_MS,
    CONF_RAIN_CLOSE_DELAY_MIN,
    CONF_RAIN_SENSOR,
    CONF_SAFETY_CLOSE_DELAY_S,
    CONF_SAFETY_ENABLED,
    CONF_SAFETY_VIBRATION_S,
    CONF_TRAVEL_TIME_S,
    CONF_VENTILATION_CHECK_INTERVAL,
    CONF_VENTILATION_OPEN_S,
    CONF_VIBRATION_SENSOR,
    DEFAULT_AH_DIFF_THRESHOLD,
    DEFAULT_HUMIDITY_THRESHOLD,
    DEFAULT_PULSE_DELAY_S,
    DEFAULT_PULSE_DURATION_MS,
    DEFAULT_RAIN_CLOSE_DELAY_MIN,
    DEFAULT_SAFETY_CLOSE_DELAY_S,
    DEFAULT_SAFETY_VIBRATION_S,
    DEFAULT_TRAVEL_TIME_S,
    DEFAULT_VENTILATION_CHECK_INTERVAL,
    DEFAULT_VENTILATION_OPEN_S,
    DOMAIN,
)

_SUG = {
    CONF_CONTROL_SWITCH: "switch.hm_schaltaktor_garagentor",
    CONF_CLOSED_SENSOR: "binary_sensor.hm_schalter_taster_garage_ch1",
    CONF_OPEN_SENSOR: "binary_sensor.hm_schalter_taster_garage_ch2",
    CONF_VIBRATION_SENSOR: "binary_sensor.hm_neigungssensor_garage_bewegung",
    CONF_EXTERNAL_BUTTON: "event.hm_pbi_4_fm_req1243481_garage_hm_taster_garage_taster3",
    CONF_INDOOR_TEMP_SENSOR: "sensor.hm_temp_feuchte_garage_temperatur",
    CONF_INDOOR_HUMIDITY_SENSOR: "sensor.hm_temp_feuchte_garage_luftfeuchtigkeit",
    CONF_OUTDOOR_TEMP_SENSOR: "sensor.hm_temp_feuchte_aussen_temp_feuchte_aussen_temperatur",
    CONF_OUTDOOR_HUMIDITY_SENSOR: "sensor.hm_temp_feuchte_aussen_temp_feuchte_aussen_luftfeuchtigkeit",
    CONF_RAIN_SENSOR: "binary_sensor.regensensor_rain",
    CONF_PRESENCE_ENTITY: "group.allepersonen",
}


def _e(d):
    """Create entity selector."""
    return selector.EntitySelector(selector.EntitySelectorConfig(domain=d if isinstance(d, list) else [d]))


def _n(mn, mx, s, u, m="box"):
    """Create number selector."""
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=mn,
            max=mx,
            step=s,
            unit_of_measurement=u,
            mode=selector.NumberSelectorMode.BOX if m == "box" else selector.NumberSelectorMode.SLIDER,
        )
    )


def _s(k):
    """Return suggested_value description dict."""
    v = _SUG.get(k)
    return {"suggested_value": v} if v else {}


class SmartGarageConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Garage."""

    VERSION = 3

    def __init__(self) -> None:
        """Initialize flow."""
        self._data: dict[str, Any] = {}

    async def async_step_user(self, ui: dict[str, Any] | None = None):
        """Step 1: Basic settings."""
        if ui is not None:
            # Phase 1.2: Prevent duplicate config entries for same switch
            await self.async_set_unique_id(ui[CONF_CONTROL_SWITCH])
            self._abort_if_unique_id_configured()

            self._data.update(ui)
            return await self.async_step_sensors()

        lang = self.hass.config.language if self.hass else "de"
        dn = "Garagentor" if lang.startswith("de") else "Garage Door"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=dn): str,
                    vol.Required(CONF_CONTROL_SWITCH, description=_s(CONF_CONTROL_SWITCH)): _e(["switch", "button"]),
                    vol.Optional(CONF_PULSE_DURATION_MS, default=DEFAULT_PULSE_DURATION_MS): _n(100, 5000, 50, "ms"),
                    vol.Optional(CONF_PULSE_DELAY_S, default=DEFAULT_PULSE_DELAY_S): _n(0.5, 10, 0.5, "s", "slider"),
                }
            ),
        )

    async def async_step_sensors(self, ui: dict[str, Any] | None = None):
        """Step 2: Position sensors."""
        if ui is not None:
            self._data.update(ui)
            return await self.async_step_safety()
        return self.async_show_form(
            step_id="sensors",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_CLOSED_SENSOR, description=_s(CONF_CLOSED_SENSOR)): _e("binary_sensor"),
                    vol.Optional(CONF_CLOSED_SENSOR_INVERT, default=True): selector.BooleanSelector(),
                    vol.Optional(CONF_OPEN_SENSOR, description=_s(CONF_OPEN_SENSOR)): _e("binary_sensor"),
                    vol.Optional(CONF_OPEN_SENSOR_INVERT, default=False): selector.BooleanSelector(),
                    vol.Optional(CONF_VIBRATION_SENSOR, description=_s(CONF_VIBRATION_SENSOR)): _e("binary_sensor"),
                    vol.Optional(CONF_TRAVEL_TIME_S, default=DEFAULT_TRAVEL_TIME_S): _n(5, 60, 1, "s", "slider"),
                    vol.Optional(CONF_EXTERNAL_BUTTON, description=_s(CONF_EXTERNAL_BUTTON)): _e(
                        ["event", "binary_sensor"]
                    ),
                }
            ),
        )

    async def async_step_safety(self, ui: dict[str, Any] | None = None):
        """Step 3: Safety settings."""
        if ui is not None:
            self._data.update(ui)
            return await self.async_step_ventilation()
        return self.async_show_form(
            step_id="safety",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_SAFETY_ENABLED, default=True): selector.BooleanSelector(),
                    vol.Optional(CONF_SAFETY_VIBRATION_S, default=DEFAULT_SAFETY_VIBRATION_S): _n(
                        3, 30, 1, "s", "slider"
                    ),
                    vol.Optional(CONF_SAFETY_CLOSE_DELAY_S, default=DEFAULT_SAFETY_CLOSE_DELAY_S): _n(
                        5, 60, 5, "s", "slider"
                    ),
                    vol.Optional(CONF_NOTIFY_SERVICE, default=""): str,
                }
            ),
        )

    async def async_step_ventilation(self, ui: dict[str, Any] | None = None):
        """Step 4: Ventilation toggle."""
        if ui is not None:
            self._data.update(ui)
            if ui.get(CONF_ENABLE_VENTILATION):
                return await self.async_step_ventilation_sensors()
            return self.async_create_entry(
                title=self._data.get(CONF_NAME, "Smart Garage"),
                data=self._data,
            )
        return self.async_show_form(
            step_id="ventilation",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_ENABLE_VENTILATION, default=True): selector.BooleanSelector(),
                }
            ),
        )

    async def async_step_ventilation_sensors(self, ui: dict[str, Any] | None = None):
        """Step 5: Climate sensors and thresholds."""
        if ui is not None:
            self._data.update(ui)
            return self.async_create_entry(
                title=self._data.get(CONF_NAME, "Smart Garage"),
                data=self._data,
            )
        return self.async_show_form(
            step_id="ventilation_sensors",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_INDOOR_TEMP_SENSOR, description=_s(CONF_INDOOR_TEMP_SENSOR)): _e("sensor"),
                    vol.Optional(CONF_INDOOR_HUMIDITY_SENSOR, description=_s(CONF_INDOOR_HUMIDITY_SENSOR)): _e(
                        "sensor"
                    ),
                    vol.Optional(CONF_OUTDOOR_TEMP_SENSOR, description=_s(CONF_OUTDOOR_TEMP_SENSOR)): _e("sensor"),
                    vol.Optional(CONF_OUTDOOR_HUMIDITY_SENSOR, description=_s(CONF_OUTDOOR_HUMIDITY_SENSOR)): _e(
                        "sensor"
                    ),
                    vol.Optional(CONF_RAIN_SENSOR, description=_s(CONF_RAIN_SENSOR)): _e("binary_sensor"),
                    vol.Optional(CONF_HUMIDITY_THRESHOLD, default=DEFAULT_HUMIDITY_THRESHOLD): _n(
                        30, 90, 1, "%", "slider"
                    ),
                    vol.Optional(CONF_AH_DIFF_THRESHOLD, default=DEFAULT_AH_DIFF_THRESHOLD): _n(0.5, 15, 0.5, "g/m³"),
                    vol.Optional(CONF_VENTILATION_OPEN_S, default=DEFAULT_VENTILATION_OPEN_S): _n(
                        0.5, 10, 0.5, "s", "slider"
                    ),
                    vol.Optional(CONF_VENTILATION_CHECK_INTERVAL, default=DEFAULT_VENTILATION_CHECK_INTERVAL): _n(
                        5, 60, 5, "min", "slider"
                    ),
                    vol.Optional(CONF_PRESENCE_ENTITY, description=_s(CONF_PRESENCE_ENTITY)): _e(
                        ["group", "person", "binary_sensor"]
                    ),
                    vol.Optional(CONF_RAIN_CLOSE_DELAY_MIN, default=DEFAULT_RAIN_CLOSE_DELAY_MIN): _n(
                        0, 15, 1, "min", "slider"
                    ),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow handler."""
        return SmartGarageOptionsFlow(entry)


class SmartGarageOptionsFlow(OptionsFlow):
    """Handle options for Smart Garage (menu-based)."""

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._entry = entry
        self._data: dict[str, Any] = dict(entry.data)

    def _d(self, k, d=None):
        """Get config value with default."""
        return self._data.get(k, d)

    def _save(self):
        """Save config and create entry."""
        self.hass.config_entries.async_update_entry(self._entry, data=self._data)
        return self.async_create_entry(title="", data={})

    async def async_step_init(self, ui=None):
        """Show options menu."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["opt_basic", "opt_sensors", "opt_safety", "opt_ventilation"],
        )

    async def async_step_opt_basic(self, ui=None):
        """Basic settings."""
        if ui:
            self._data.update(ui)
            return self._save()
        return self.async_show_form(
            step_id="opt_basic",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_CONTROL_SWITCH, default=self._d(CONF_CONTROL_SWITCH)): _e(["switch", "button"]),
                    vol.Optional(
                        CONF_PULSE_DURATION_MS, default=self._d(CONF_PULSE_DURATION_MS, DEFAULT_PULSE_DURATION_MS)
                    ): _n(100, 5000, 50, "ms"),
                    vol.Optional(CONF_PULSE_DELAY_S, default=self._d(CONF_PULSE_DELAY_S, DEFAULT_PULSE_DELAY_S)): _n(
                        0.5, 10, 0.5, "s", "slider"
                    ),
                }
            ),
        )

    async def async_step_opt_sensors(self, ui=None):
        """Position sensors."""
        if ui:
            self._data.update(ui)
            return self._save()
        return self.async_show_form(
            step_id="opt_sensors",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_CLOSED_SENSOR, description={"suggested_value": self._d(CONF_CLOSED_SENSOR)}): _e(
                        "binary_sensor"
                    ),
                    vol.Optional(
                        CONF_CLOSED_SENSOR_INVERT, default=self._d(CONF_CLOSED_SENSOR_INVERT, True)
                    ): selector.BooleanSelector(),
                    vol.Optional(CONF_OPEN_SENSOR, description={"suggested_value": self._d(CONF_OPEN_SENSOR)}): _e(
                        "binary_sensor"
                    ),
                    vol.Optional(
                        CONF_OPEN_SENSOR_INVERT, default=self._d(CONF_OPEN_SENSOR_INVERT, False)
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_VIBRATION_SENSOR, description={"suggested_value": self._d(CONF_VIBRATION_SENSOR)}
                    ): _e("binary_sensor"),
                    vol.Optional(CONF_TRAVEL_TIME_S, default=self._d(CONF_TRAVEL_TIME_S, DEFAULT_TRAVEL_TIME_S)): _n(
                        5, 60, 1, "s", "slider"
                    ),
                    vol.Optional(
                        CONF_EXTERNAL_BUTTON, description={"suggested_value": self._d(CONF_EXTERNAL_BUTTON)}
                    ): _e(["event", "binary_sensor"]),
                }
            ),
        )

    async def async_step_opt_safety(self, ui=None):
        """Safety settings."""
        if ui:
            self._data.update(ui)
            return self._save()
        return self.async_show_form(
            step_id="opt_safety",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SAFETY_ENABLED, default=self._d(CONF_SAFETY_ENABLED, True)
                    ): selector.BooleanSelector(),
                    vol.Optional(
                        CONF_SAFETY_VIBRATION_S, default=self._d(CONF_SAFETY_VIBRATION_S, DEFAULT_SAFETY_VIBRATION_S)
                    ): _n(3, 30, 1, "s", "slider"),
                    vol.Optional(
                        CONF_SAFETY_CLOSE_DELAY_S,
                        default=self._d(CONF_SAFETY_CLOSE_DELAY_S, DEFAULT_SAFETY_CLOSE_DELAY_S),
                    ): _n(5, 60, 5, "s", "slider"),
                    vol.Optional(CONF_NOTIFY_SERVICE, default=self._d(CONF_NOTIFY_SERVICE, "")): str,
                }
            ),
        )

    async def async_step_opt_ventilation(self, ui=None):
        """Ventilation toggle."""
        if ui:
            self._data.update(ui)
            if ui.get(CONF_ENABLE_VENTILATION):
                return await self.async_step_opt_vent_sensors()
            for k in [
                CONF_INDOOR_TEMP_SENSOR,
                CONF_INDOOR_HUMIDITY_SENSOR,
                CONF_OUTDOOR_TEMP_SENSOR,
                CONF_OUTDOOR_HUMIDITY_SENSOR,
                CONF_RAIN_SENSOR,
                CONF_HUMIDITY_THRESHOLD,
                CONF_AH_DIFF_THRESHOLD,
                CONF_VENTILATION_OPEN_S,
                CONF_VENTILATION_CHECK_INTERVAL,
                CONF_PRESENCE_ENTITY,
                CONF_RAIN_CLOSE_DELAY_MIN,
            ]:
                self._data.pop(k, None)
            return self._save()
        return self.async_show_form(
            step_id="opt_ventilation",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ENABLE_VENTILATION, default=self._d(CONF_ENABLE_VENTILATION, False)
                    ): selector.BooleanSelector(),
                }
            ),
        )

    async def async_step_opt_vent_sensors(self, ui=None):
        """Ventilation sensor config."""
        if ui:
            self._data.update(ui)
            return self._save()
        return self.async_show_form(
            step_id="opt_vent_sensors",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_INDOOR_TEMP_SENSOR, description={"suggested_value": self._d(CONF_INDOOR_TEMP_SENSOR)}
                    ): _e("sensor"),
                    vol.Optional(
                        CONF_INDOOR_HUMIDITY_SENSOR,
                        description={"suggested_value": self._d(CONF_INDOOR_HUMIDITY_SENSOR)},
                    ): _e("sensor"),
                    vol.Optional(
                        CONF_OUTDOOR_TEMP_SENSOR, description={"suggested_value": self._d(CONF_OUTDOOR_TEMP_SENSOR)}
                    ): _e("sensor"),
                    vol.Optional(
                        CONF_OUTDOOR_HUMIDITY_SENSOR,
                        description={"suggested_value": self._d(CONF_OUTDOOR_HUMIDITY_SENSOR)},
                    ): _e("sensor"),
                    vol.Optional(CONF_RAIN_SENSOR, description={"suggested_value": self._d(CONF_RAIN_SENSOR)}): _e(
                        "binary_sensor"
                    ),
                    vol.Optional(
                        CONF_HUMIDITY_THRESHOLD, default=self._d(CONF_HUMIDITY_THRESHOLD, DEFAULT_HUMIDITY_THRESHOLD)
                    ): _n(30, 90, 1, "%", "slider"),
                    vol.Optional(
                        CONF_AH_DIFF_THRESHOLD, default=self._d(CONF_AH_DIFF_THRESHOLD, DEFAULT_AH_DIFF_THRESHOLD)
                    ): _n(0.5, 15, 0.5, "g/m³"),
                    vol.Optional(
                        CONF_VENTILATION_OPEN_S, default=self._d(CONF_VENTILATION_OPEN_S, DEFAULT_VENTILATION_OPEN_S)
                    ): _n(0.5, 10, 0.5, "s", "slider"),
                    vol.Optional(
                        CONF_VENTILATION_CHECK_INTERVAL,
                        default=self._d(CONF_VENTILATION_CHECK_INTERVAL, DEFAULT_VENTILATION_CHECK_INTERVAL),
                    ): _n(5, 60, 5, "min", "slider"),
                    vol.Optional(
                        CONF_PRESENCE_ENTITY, description={"suggested_value": self._d(CONF_PRESENCE_ENTITY)}
                    ): _e(["group", "person", "binary_sensor"]),
                    vol.Optional(
                        CONF_RAIN_CLOSE_DELAY_MIN,
                        default=self._d(CONF_RAIN_CLOSE_DELAY_MIN, DEFAULT_RAIN_CLOSE_DELAY_MIN),
                    ): _n(0, 15, 1, "min", "slider"),
                }
            ),
        )
