from __future__ import annotations

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_PASSWORD, CONF_USERNAME

TO_REDACT = {CONF_PASSWORD, CONF_USERNAME}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "data": list(coordinator.data.values()),
    }
