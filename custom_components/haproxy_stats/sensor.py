from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfInformation
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_DATA_SIZE_UNIT,
    DATA_SIZE_UNIT_FACTORS,
    DEFAULT_DATA_SIZE_UNIT,
)
from .coordinator import HAProxyStatsCoordinator
from .entity import HAProxyStatsEntity

HA_DATA_SIZE_UNITS = {
    "B": UnitOfInformation.BYTES,
    "kB": UnitOfInformation.KILOBYTES,
    "MB": UnitOfInformation.MEGABYTES,
    "GB": UnitOfInformation.GIGABYTES,
    "TB": UnitOfInformation.TERABYTES,
}


@dataclass(frozen=True, kw_only=True)
class HAProxySensorEntityDescription(SensorEntityDescription):
    parse_int: bool = True
    is_data_size: bool = False


SENSOR_DESCRIPTIONS: tuple[HAProxySensorEntityDescription, ...] = (
    HAProxySensorEntityDescription(
        key="scur",
        translation_key="sessions",
        name="Sessions",
        icon="mdi:account-multiple",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAProxySensorEntityDescription(
        key="smax",
        translation_key="sessions_max",
        name="Max Sessions",
        icon="mdi:account-multiple-plus",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAProxySensorEntityDescription(
        key="stot",
        translation_key="sessions_total",
        name="Total Sessions",
        icon="mdi:counter",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    HAProxySensorEntityDescription(
        key="bin",
        translation_key="bytes_in",
        name="Bytes In",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        state_class=SensorStateClass.TOTAL_INCREASING,
        parse_int=False,
        is_data_size=True,
        suggested_display_precision=2,
    ),
    HAProxySensorEntityDescription(
        key="bout",
        translation_key="bytes_out",
        name="Bytes Out",
        device_class=SensorDeviceClass.DATA_SIZE,
        native_unit_of_measurement=UnitOfInformation.MEGABYTES,
        state_class=SensorStateClass.TOTAL_INCREASING,
        parse_int=False,
        is_data_size=True,
        suggested_display_precision=2,
    ),
    HAProxySensorEntityDescription(
        key="rate",
        translation_key="session_rate",
        name="Session Rate",
        icon="mdi:speedometer",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    HAProxySensorEntityDescription(
        key="ereq",
        translation_key="errors_request",
        name="Request Errors",
        icon="mdi:alert-circle",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    HAProxySensorEntityDescription(
        key="eresp",
        translation_key="errors_response",
        name="Response Errors",
        icon="mdi:alert-circle-outline",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    HAProxySensorEntityDescription(
        key="econ",
        translation_key="errors_connection",
        name="Connection Errors",
        icon="mdi:alert-circle",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    HAProxySensorEntityDescription(
        key="wretr",
        translation_key="warnings_retries",
        name="Retry Warnings",
        icon="mdi:alert-circle",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    HAProxySensorEntityDescription(
        key="wredis",
        translation_key="warnings_redispatch",
        name="Redispatch Warnings",
        icon="mdi:alert-circle",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: HAProxyStatsCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    entities_known: set[str] = hass.data[DOMAIN][entry.entry_id]["entities_known"]

    entities: list[HAProxyStatsSensor] = []

    for row_key in coordinator.data:
        for description in SENSOR_DESCRIPTIONS:
            unique_id = f"{entry.entry_id}_{row_key}_{description.key}"
            if unique_id in entities_known:
                continue
            entities.append(HAProxyStatsSensor(coordinator, entry, row_key, description))
            entities_known.add(unique_id)

    async_add_entities(entities)


class HAProxyStatsSensor(HAProxyStatsEntity, SensorEntity):
    def __init__(
        self,
        coordinator: HAProxyStatsCoordinator,
        entry: ConfigEntry,
        row_key: str,
        description: HAProxySensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, entry, row_key, description)
        self._attr_unique_id = f"{entry.entry_id}_{row_key}_{description.key}"
        self._data_size_unit = entry.options.get(
            CONF_DATA_SIZE_UNIT,
            entry.data.get(CONF_DATA_SIZE_UNIT, DEFAULT_DATA_SIZE_UNIT),
        )

    @property
    def native_unit_of_measurement(self):
        if (
            isinstance(self.entity_description, HAProxySensorEntityDescription)
            and self.entity_description.is_data_size
        ):
            return HA_DATA_SIZE_UNITS.get(
                self._data_size_unit,
                UnitOfInformation.MEGABYTES,
            )

        return self.entity_description.native_unit_of_measurement

    @property
    def native_value(self):
        row = self._row
        if row is None:
            return None

        raw = row.get(self.entity_description.key)
        if raw in (None, ""):
            return None

        if (
            isinstance(self.entity_description, HAProxySensorEntityDescription)
            and self.entity_description.is_data_size
        ):
            try:
                bytes_value = float(raw)
                factor = DATA_SIZE_UNIT_FACTORS.get(self._data_size_unit)
                if not factor:
                    return None
                return bytes_value / factor
            except ValueError:
                return None

        if (
            isinstance(self.entity_description, HAProxySensorEntityDescription)
            and self.entity_description.parse_int
        ):
            try:
                return int(float(raw))
            except ValueError:
                return None

        return raw
