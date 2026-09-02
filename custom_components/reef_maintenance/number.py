"""Interval slider of a maintenance task."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_BRAND, DOMAIN
from .entity import ReefMaintenanceEntity
from .storage import Equipment, MaintenanceStore, TaskInstance
from .tasks import DAYS_PER_UNIT


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    store: MaintenanceStore = data["store"]
    brand: str = entry.data[CONF_BRAND]
    brand_dev_id: str = data["brand_device_id"]

    async_add_entities(
        ReefMaintenanceIntervalNumber(
            store, brand, equipment, instance, via_device_id=brand_dev_id
        )
        for equipment in data["equipments"]
        for instance in equipment.tasks
    )


class ReefMaintenanceIntervalNumber(ReefMaintenanceEntity, NumberEntity):  # type: ignore[misc]
    """Slider exposing the interval of one task.

    Storage is always in days; this entity is the only place that converts to
    and from the task's display unit. The unit travels in the translation_key
    (hence in `reef_role`, e.g. "maint_pump_clean_interval_weeks"), which is
    how ha-reef-card knows what the value means without an extra attribute.
    """

    _attr_icon = "mdi:calendar-range"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_mode = NumberMode.SLIDER
    _attr_native_step = 1.0
    _attr_suggested_display_precision = 0

    def __init__(
        self,
        store: MaintenanceStore,
        brand: str,
        equipment: Equipment,
        instance: TaskInstance,
        *,
        via_device_id: str | None = None,
    ) -> None:
        task = instance.task
        super().__init__(
            store,
            brand,
            equipment,
            instance,
            "interval",
            f"_interval_{task.unit}",
            via_device_id=via_device_id,
        )
        # "days" must be listed explicitly in DAYS_PER_UNIT, otherwise a task
        # declared in days would silently be stored as weeks.
        self._unit_factor = DAYS_PER_UNIT.get(task.unit, 7)
        self._attr_native_min_value = float(task.min_days // self._unit_factor)
        self._attr_native_max_value = float(task.max_days // self._unit_factor)

    @property
    def native_value(self) -> float | None:  # pyright: ignore[reportIncompatibleVariableOverride]
        days = self._store.get_interval(
            self._equipment.id, self._task.key, self._task.default_days
        )
        return float(days // self._unit_factor)

    async def async_set_native_value(self, value: float) -> None:
        days = round(value) * self._unit_factor
        await self._store.async_set_interval(self._equipment.id, self._task.key, days)
