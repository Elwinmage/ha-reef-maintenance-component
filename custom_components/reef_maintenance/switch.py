"""Per-task notification opt-out."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

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
        ReefMaintenanceNotifySwitch(store, brand, equipment, instance)
        for equipment in data["equipments"]
        for instance in equipment.tasks
    )


class ReefMaintenanceNotifySwitch(ReefMaintenanceEntity, SwitchEntity):  # type: ignore[misc]
    """Enables or disables overdue alerts for one task.

    The value is mirrored in the button's `notify` attribute, so the alert
    blueprint never has to correlate two entities.
    """

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        store: MaintenanceStore,
        brand: str,
        equipment: Equipment,
        instance: TaskInstance,
    ) -> None:
        super().__init__(store, brand, equipment, instance, "notify", "_notify")
        # State is mirrored into `_attr_*` rather than exposed through
        # properties: SwitchEntity declares is_on and icon as cached_property.
        self._attr_is_on = True
        self._attr_icon = "mdi:bell-ring"

    def _refresh_state(self) -> None:
        enabled = self._store.get_notify(self._equipment.id, self._task.key)
        self._attr_is_on = enabled
        self._attr_icon = "mdi:bell-ring" if enabled else "mdi:bell-off"

    def _on_store_change(self) -> None:
        self._refresh_state()
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        # Read the persisted value before the first state is written, else a
        # muted task briefly shows up as enabled.
        self._refresh_state()
        await super().async_added_to_hass()

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._store.async_set_notify(self._equipment.id, self._task.key, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._store.async_set_notify(self._equipment.id, self._task.key, False)
