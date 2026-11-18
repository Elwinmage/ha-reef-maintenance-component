"""Action button recording that a maintenance task has been done."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .catalog import is_catalog_entry
from .catalog_runtime import catalog_entities
from .const import CONF_BRAND, DOMAIN
from .entity import ReefMaintenanceEntity
from .storage import Equipment, MaintenanceStore, TaskInstance, compute_days_left


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    # The dedicated catalog entry carries the "update now" button; a brand
    # entry carries one "done" button per task.
    if is_catalog_entry(entry):
        async_add_entities(catalog_entities(hass, entry, DOMAIN, "button"))
        return

    data = hass.data[DOMAIN][entry.entry_id]
    store: MaintenanceStore = data["store"]
    brand: str = entry.data[CONF_BRAND]
    brand_dev_id: str = data["brand_device_id"]

    entities = [
        ReefMaintenanceButton(
            store, brand, equipment, instance, via_device_id=brand_dev_id
        )
        for equipment in data["equipments"]
        for instance in equipment.tasks
    ]
    async_add_entities(entities)


class ReefMaintenanceButton(ReefMaintenanceEntity, ButtonEntity):  # type: ignore[misc]
    """Button that stamps "done now" on a maintenance task.

    It carries every derived value as state attributes, so this single entity
    is enough for both the alert blueprint and the ha-reef-card maintenance
    view:

      reef_role     : "maint_<task>"  (added by ReefRoleMixin)
      task_key      : task identifier
      interval_days : configured interval, in days
      days_left     : remaining days, negative when overdue, None if never reset
      overdue       : boolean
      last_reset    : ISO-8601 timestamp, or None
      notify        : mirror of the companion notification switch
    """

    def __init__(
        self,
        store: MaintenanceStore,
        brand: str,
        equipment: Equipment,
        instance: TaskInstance,
        *,
        via_device_id: str | None = None,
    ) -> None:
        super().__init__(
            store, brand, equipment, instance, "action", via_device_id=via_device_id
        )
        self._attr_icon = instance.task.icon

    def _compute_attrs(self) -> dict[str, object]:
        equipment_id = self._equipment.id
        key = self._task.key
        last = self._store.get_last_reset(equipment_id, key)
        interval = self._store.get_interval(equipment_id, key, self._task.default_days)
        days_left = compute_days_left(last, interval)
        attrs: dict[str, object] = {
            "last_reset": last.isoformat() if last is not None else None,
            "interval_days": interval,
            "days_left": days_left,
            "overdue": days_left is not None and days_left < 0,
            "task_key": key,
            "notify": self._store.get_notify(equipment_id, key),
        }
        return attrs

    @property
    def extra_state_attributes(self) -> dict[str, object] | None:  # pyright: ignore[reportIncompatibleVariableOverride]
        self._attr_extra_state_attributes = self._compute_attrs()
        return super().extra_state_attributes  # type: ignore[misc]

    async def async_press(self) -> None:
        """Record a reset; the store notifies our listener to refresh."""
        await self._store.async_reset(self._equipment.id, self._task.key)
