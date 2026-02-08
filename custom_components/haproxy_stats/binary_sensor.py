from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import HAProxyStatsCoordinator
from .entity import HAProxyStatsEntity

UP_STATUSES = {
    "UP",
    "OPEN",
    "OPENING",
    "READY",
    "L4OK",
    "L6OK",
    "L7OK",
}

DOWN_STATUSES = {
    "DOWN",
    "MAINT",
    "NOLB",
    "STOP",
    "STOPPED",
    "CLOSED",
}


@dataclass(frozen=True, kw_only=True)
class HAProxyBinarySensorEntityDescription(BinarySensorEntityDescription):
    pass


BINARY_SENSOR_DESCRIPTIONS: tuple[HAProxyBinarySensorEntityDescription, ...] = (
    HAProxyBinarySensorEntityDescription(
        key="status",
        translation_key="availability",
        name="Available",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HAProxyStatsCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities_known: set[str] = hass.data[DOMAIN][entry.entry_id]["entities_known"]

    entities: list[HAProxyStatsBinarySensor] = []

    for row_key in coordinator.data:
        for description in BINARY_SENSOR_DESCRIPTIONS:
            unique_id = f"{entry.entry_id}_{row_key}_{description.key}"
            if unique_id in entities_known:
                continue
            entities.append(HAProxyStatsBinarySensor(coordinator, entry, row_key, description))
            entities_known.add(unique_id)

    async_add_entities(entities)


class HAProxyStatsBinarySensor(HAProxyStatsEntity, BinarySensorEntity):
    def __init__(
        self,
        coordinator: HAProxyStatsCoordinator,
        entry: ConfigEntry,
        row_key: str,
        description: HAProxyBinarySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, entry, row_key, description)
        self._attr_unique_id = f"{entry.entry_id}_{row_key}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        row = self._row
        if row is None:
            return None

        status = (row.get("status") or "").upper()
        if not status:
            return None

        if status in UP_STATUSES or status.startswith("UP"):
            return True
        if status in DOWN_STATUSES:
            return False

        return None

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        row = self._row
        if row is None:
            return None

        status = row.get("status")
        if not status:
            return None

        return {"status": status}
