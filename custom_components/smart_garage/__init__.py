"""Smart Garage – custom integration for impulse-based garage doors."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, PLATFORMS
from .controller import SmartGarageController

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    controller = SmartGarageController(hass, entry.entry_id, dict(entry.data))
    hass.data[DOMAIN][entry.entry_id] = controller
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await controller.async_start()
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True

async def _async_update_listener(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry) -> bool:
    ctrl = hass.data[DOMAIN].get(entry.entry_id)
    if ctrl: await ctrl.async_stop()
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok: hass.data[DOMAIN].pop(entry.entry_id, None)
    return ok
