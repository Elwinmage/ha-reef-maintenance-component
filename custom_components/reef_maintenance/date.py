"""Date entity letting the user backdate the last maintenance.

This is the entity that makes the integration usable on day one: without it,
every task starts from "never done" the day the equipment is added, and three
months later a dozen tasks fall due on the same afternoon. Setting the real
last date spreads them out immediately.
"""

from __future__ import annotations

from datetime import date, datetime, time

from homeassistant.components.date import DateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import CONF_BRAND, DOMAIN
from .entity import ReefMaintenanceEntity
from .storage import Equipment, MaintenanceStore, TaskInstance


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    store: MaintenanceStore = data["store"]
    brand: str = entry.data[CONF_BRAND]

    async_add_entities(
        ReefMaintenanceLastResetDate(store, brand, equipment, instance)
        for equipment in data["equipments"]
        for instance in equipment.tasks
    )


class ReefMaintenanceLastResetDate(ReefMaintenanceEntity, DateEntity):  # type: ignore[misc]
    """Reads and writes the `last_reset` of one task, as a plain date.

    The store keeps an aware datetime; a date picked here is anchored at local
    midnight so "3 days ago" means the same thing to the user and to
    `days_left`.
    """

    _attr_icon = "mdi:calendar-check"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        store: MaintenanceStore,
        brand: str,
        equipment: Equipment,
        instance: TaskInstance,
    ) -> None:
        super().__init__(store, brand, equipment, instance, "last_reset", "_last_reset")

    @property
    def native_value(self) -> date | None:  # pyright: ignore[reportIncompatibleVariableOverride]
        stamp = self._store.get_last_reset(self._equipment.id, self._task.key)
        if stamp is None:
            return None
        # Stored in UTC, shown in the user's timezone: without the conversion
        # a late-evening reset would display as the next day.
        return dt_util.as_local(stamp).date()

    async def async_set_value(self, value: date) -> None:
        local_midnight = datetime.combine(
            value, time.min, dt_util.get_default_time_zone()
        )
        await self._store.async_reset(
            self._equipment.id, self._task.key, dt_util.as_utc(local_midnight)
        )
