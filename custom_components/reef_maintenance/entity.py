"""Base entity classes.

Everything here exists to publish one contract: the `reef_role` state
attribute, shared with ha-reefbeat-component and ha-aquamedic-component. It is
what makes these tasks show up in the ha-reef-card maintenance view with no
card-side change, and what the alert blueprints target.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .storage import Equipment, MaintenanceStore, TaskInstance
from .tasks import CUSTOM_TASK, ROLE_PREFIX, MaintenanceTask


def brand_device_id(brand: str) -> str:
    """Return the identifier of the per-brand hub device."""
    return f"brand_{brand}"


class ReefRoleMixin:
    """Expose a stable `reef_role` state attribute.

    `reef_role` is built from the task key (`maint_<task>`), not from the
    display translation_key: catalog tasks are named generically through a
    placeholder, but their role must stay task-specific — it is the contract
    ha-reef-card and the alert blueprints read.

    Must come FIRST in the MRO so this property wins over the default
    `Entity` one while still picking up `_attr_extra_state_attributes`.
    """

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        base = getattr(self, "_attr_extra_state_attributes", None) or {}
        role = getattr(self, "_reef_role", None) or getattr(
            self, "translation_key", None
        )
        if role:
            return {**base, "reef_role": role}
        return dict(base) if base else None


class ReefMaintenanceEntity(ReefRoleMixin, Entity):  # type: ignore[misc]
    """Common plumbing for the four entities of a maintenance task.

    There is no coordinator: this integration talks to nothing. State comes
    from the local Store, and entities refresh through its listeners.
    """

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        store: MaintenanceStore,
        brand: str,
        equipment: Equipment,
        instance: TaskInstance,
        unique_suffix: str,
        translation_suffix: str = "",
        *,
        via_device_id: str | None = None,
    ) -> None:
        self._store = store
        self._equipment = equipment
        self._instance = instance
        self._task: MaintenanceTask = instance.task

        self._attr_unique_id = f"{equipment.id}_{self._task.key}_{unique_suffix}"
        # reef_role stays task-specific (maint_<task><suffix>), the shared
        # contract ha-reef-card and the blueprints read.
        self._reef_role = f"{ROLE_PREFIX}{self._task.key}{translation_suffix}"
        # Catalog and user-defined tasks carry a label: they reuse the generic
        # `maint_custom` keys, and the label travels as a placeholder instead of
        # a translation. Only the fixed suffix ("(weeks)", "(last done)") stays
        # translated. Everything else has a label, so this is the normal path.
        if instance.label is not None:
            base_key = CUSTOM_TASK.translation_key
            self._attr_translation_placeholders = {"task": instance.label}
        else:
            base_key = self._task.translation_key
        self._attr_translation_key = f"{base_key}{translation_suffix}"

        di = DeviceInfo(
            identifiers={(DOMAIN, equipment.id)},
            name=equipment.name,
            manufacturer=brand.capitalize(),
            model=equipment.model,
        )
        if via_device_id is not None:
            di["via_device_id"] = via_device_id
        self._attr_device_info = di
        self._unsub: Callable[[], None] | None = None

    # ---- lifecycle -------------------------------------------------------

    def _on_store_change(self) -> None:
        """React to a change of this instance's stored state."""
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()

        @callback
        def _changed() -> None:
            self._on_store_change()

        self._unsub = self._store.async_add_listener(
            self._equipment.id, self._task.key, _changed
        )

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub is not None:
            self._unsub()
            self._unsub = None
        await super().async_will_remove_from_hass()
