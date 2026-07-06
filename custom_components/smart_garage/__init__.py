"""Smart Garage – custom integration for impulse-based garage doors."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, PLATFORMS, CONF_CONTROL_SWITCH
from .controller import SmartGarageController

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Garage from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Phase 1.1: Verify control switch exists before setup
    control_switch = entry.data.get(CONF_CONTROL_SWITCH)
    if control_switch and hass.states.get(control_switch) is None:
        raise ConfigEntryNotReady(
            f"Control switch '{control_switch}' not available yet. "
            "Retrying setup..."
        )

    controller = SmartGarageController(hass, entry.entry_id, dict(entry.data))
    hass.data[DOMAIN][entry.entry_id] = controller

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await controller.async_start()

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    _LOGGER.info("Smart Garage '%s' setup complete", entry.title)

    return True


async def _async_update_listener(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Handle options update – reload the entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Unload a config entry."""
    ctrl: SmartGarageController | None = hass.data[DOMAIN].get(entry.entry_id)
    if ctrl:
        await ctrl.async_stop()

    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return ok
