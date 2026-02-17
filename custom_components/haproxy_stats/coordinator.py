from __future__ import annotations

import csv
import logging

import async_timeout
from aiohttp import BasicAuth

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_URL,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_VERIFY_SSL,
)

_LOGGER = logging.getLogger(__name__)


class HAProxyStatsCoordinator(DataUpdateCoordinator[dict[str, dict[str, str]]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, update_interval) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.entry = entry

    async def _async_update_data(self) -> dict[str, dict[str, str]]:
        url = self.entry.data[CONF_URL]
        username = self.entry.data.get(CONF_USERNAME)
        password = self.entry.data.get(CONF_PASSWORD)
        verify_ssl = self.entry.options.get(
            CONF_VERIFY_SSL,
            self.entry.data.get(CONF_VERIFY_SSL, False),
        )

        auth = None
        if username or password:
            auth = BasicAuth(username or "", password or "")

        session = async_get_clientsession(self.hass)

        try:
            async with async_timeout.timeout(15):
                response = await session.get(url, auth=auth, ssl=verify_ssl)
                async with response:
                    if response.status != 200:
                        raise UpdateFailed(f"HTTP status {response.status}")
                    text = await response.text()
        except Exception as err:
            raise UpdateFailed(f"Error fetching HAProxy stats: {err}") from err

        return _parse_csv(text)


def _parse_csv(text: str) -> dict[str, dict[str, str]]:
    data: dict[str, dict[str, str]] = {}
    lines = [line for line in text.splitlines() if line.strip()]

    if not lines:
        return data

    header: list[str] | None = None

    for row in csv.reader(lines):
        if not row:
            continue

        if row[0].startswith("#"):
            row[0] = row[0].lstrip("# ").strip()
            header = row
            continue

        if header is None:
            continue

        if len(row) < len(header):
            row += [""] * (len(header) - len(row))

        item = dict(zip(header, row))
        pxname = item.get("pxname") or ""
        svname = item.get("svname") or ""

        if not pxname or not svname:
            continue

        key = f"{pxname}:{svname}"
        data[key] = item

    return data
