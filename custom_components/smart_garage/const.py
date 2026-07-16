"""Constants for the Smart Garage integration v1.0."""
DOMAIN = "smart_garage"

# Config keys
CONF_NAME = "name"
CONF_CONTROL_SWITCH = "control_switch"
CONF_PULSE_DURATION_MS = "pulse_duration_ms"
CONF_PULSE_DELAY_S = "pulse_delay_s"
CONF_CLOSED_SENSOR = "closed_sensor"
CONF_OPEN_SENSOR = "open_sensor"
CONF_CLOSED_SENSOR_INVERT = "closed_sensor_invert"
CONF_OPEN_SENSOR_INVERT = "open_sensor_invert"
CONF_VIBRATION_SENSOR = "vibration_sensor"
CONF_TRAVEL_TIME_S = "travel_time_s"
CONF_EXTERNAL_BUTTON = "external_button"
CONF_SAFETY_ENABLED = "safety_enabled"
CONF_SAFETY_VIBRATION_S = "safety_vibration_s"
CONF_SAFETY_CLOSE_DELAY_S = "safety_close_delay_s"
CONF_NOTIFY_SERVICE = "notify_service"
CONF_NOTIFY_TYPE = "notify_type"
CONF_NOTIFY_HA_PLUS_TARGET = "notify_ha_plus_target"
CONF_NOTIFY_HA_PLUS_SILENT = "notify_ha_plus_silent"
CONF_NOTIFY_HA_PLUS_PRIORITY = "notify_ha_plus_priority"
CONF_NOTIFY_HA_PLUS_TAG = "notify_ha_plus_tag"
CONF_ACTOR_UNREACHABLE_GRACE_S = "actor_unreachable_grace_s"
CONF_ENABLE_VENTILATION = "enable_ventilation"
CONF_INDOOR_TEMP_SENSOR = "indoor_temp_sensor"
CONF_INDOOR_HUMIDITY_SENSOR = "indoor_humidity_sensor"
CONF_OUTDOOR_TEMP_SENSOR = "outdoor_temp_sensor"
CONF_OUTDOOR_HUMIDITY_SENSOR = "outdoor_humidity_sensor"
CONF_RAIN_SENSOR = "rain_sensor"
CONF_HUMIDITY_THRESHOLD = "humidity_threshold"
CONF_AH_DIFF_THRESHOLD = "ah_diff_threshold"
CONF_VENTILATION_OPEN_S = "ventilation_open_s"
CONF_VENTILATION_CHECK_INTERVAL = "ventilation_check_interval"
CONF_PRESENCE_ENTITY = "presence_entity"
CONF_RAIN_CLOSE_DELAY_MIN = "rain_close_delay_min"

# Defaults
DEFAULT_PULSE_DURATION_MS = 300
DEFAULT_PULSE_DELAY_S = 1.0
DEFAULT_TRAVEL_TIME_S = 20
DEFAULT_SAFETY_VIBRATION_S = 7
DEFAULT_SAFETY_CLOSE_DELAY_S = 10
DEFAULT_HUMIDITY_THRESHOLD = 55
DEFAULT_AH_DIFF_THRESHOLD = 5.0
DEFAULT_VENTILATION_OPEN_S = 2.0
DEFAULT_VENTILATION_CHECK_INTERVAL = 15
DEFAULT_RAIN_CLOSE_DELAY_MIN = 4
NOTIFY_TYPE_NONE = "none"
NOTIFY_TYPE_NOTIFY = "notify"
NOTIFY_TYPE_HA_PLUS = "notify_ha_plus"
DEFAULT_NOTIFY_TYPE = NOTIFY_TYPE_NONE
DEFAULT_NOTIFY_HA_PLUS_SILENT = False
DEFAULT_NOTIFY_HA_PLUS_PRIORITY = "high"
DEFAULT_NOTIFY_HA_PLUS_TAG = "smart_garage"
DEFAULT_ACTOR_UNREACHABLE_GRACE_S = 5

# Door states
DOOR_CLOSED = "closed"
DOOR_OPENING = "opening"
DOOR_OPEN = "open"
DOOR_CLOSING = "closing"
DOOR_STOPPED_UP = "stopped_up"
DOOR_STOPPED_DOWN = "stopped_down"
DOOR_VENTILATING = "ventilating"

# Ventilation recommendation
VENT_RECOMMEND = "recommend"
VENT_NEUTRAL = "neutral"
VENT_NOT_RECOMMEND = "not_recommend"

EVENT_NOTIFICATION = f"{DOMAIN}_notification"
PLATFORMS = ["cover", "sensor", "switch", "binary_sensor"]
