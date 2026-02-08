from __future__ import annotations

import async_timeout
import voluptuous as vol
from aiohttp import BasicAuth

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_URL,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_VERIFY_SSL,
    CONF_SCAN_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_URL,
    DEFAULT_VERIFY_SSL,
    DEFAULT_SCAN_INTERVAL,
)


class CannotConnect(Exception):
    pass


async def _async_validate_input(hass: HomeAssistant, data: dict) -> None:
    url = data[CONF_URL]
    username = data.get(CONF_USERNAME)
    password = data.get(CONF_PASSWORD)
    verify_ssl = data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)

    auth = None
    if username or password:
        auth = BasicAuth(username or "", password or "")

    session = async_get_clientsession(hass)

    try:
        async with async_timeout.timeout(10):
            response = await session.get(url, auth=auth, ssl=verify_ssl)
            async with response:
                if response.status != 200:
                    raise CannotConnect
                text = await response.text()
                if "pxname" not in text:
                    raise CannotConnect
    except Exception as err:
        raise CannotConnect from err


class HAProxyStatsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await _async_validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            else:
                title = user_input.get(CONF_NAME) or DEFAULT_NAME
                return self.async_create_entry(title=title, data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_URL, default=DEFAULT_URL): str,
                vol.Optional(CONF_USERNAME): str,
                vol.Optional(CONF_PASSWORD): str,
                vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=DEFAULT_SCAN_INTERVAL,
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_import(self, user_input: dict):
        return await self.async_step_user(user_input)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return HAProxyStatsOptionsFlow(config_entry)


class HAProxyStatsOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input: dict | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.entry.options.get(
                        CONF_SCAN_INTERVAL,
                        self.entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ),
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
                vol.Optional(
                    CONF_VERIFY_SSL,
                    default=self.entry.options.get(
                        CONF_VERIFY_SSL,
                        self.entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
                    ),
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
