from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_URL


def _format_device_name(entry_title: str, pxname: str, svname: str) -> str:
    if svname in ("FRONTEND", "BACKEND", "LISTENER"):
        suffix = svname.title()
    else:
        suffix = svname

    name = f"{pxname} {suffix}".strip()

    if entry_title and entry_title not in ("HAProxy Stats", "HAProxy Stats (CSV)", "HAProxy"):
        return f"{entry_title} {name}".strip()

    return name


def _format_model_name(svname: str) -> str:
    if svname == "FRONTEND":
        return "Frontend"
    if svname == "BACKEND":
        return "Backend"
    if svname == "LISTENER":
        return "Listener"
    return "Server"


class HAProxyStatsEntity(CoordinatorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry, row_key: str, description) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._row_key = row_key

    @property
    def _row(self) -> dict[str, str] | None:
        return self.coordinator.data.get(self._row_key)

    @property
    def _pxname(self) -> str:
        row = self._row or {}
        return row.get("pxname", "HAProxy")

    @property
    def _svname(self) -> str:
        row = self._row or {}
        return row.get("svname", "")

    @property
    def device_info(self) -> DeviceInfo:
        pxname = self._pxname
        svname = self._svname
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id, pxname, svname)},
            name=_format_device_name(self._entry.title, pxname, svname),
            manufacturer="HAProxy",
            model=_format_model_name(svname),
            configuration_url=self._entry.data.get(CONF_URL),
        )
