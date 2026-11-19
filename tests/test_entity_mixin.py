"""The ReefRoleMixin on its own.

The mixin is the shared contract with ha-reefbeat-component and
ha-aquamedic-component, and its fallback paths are unreachable from the four
real entities (they all set a translation_key), so they are exercised here
directly rather than left untested.
"""

from __future__ import annotations

from custom_components.reef_maintenance.entity import ReefRoleMixin, brand_device_id


class _Bare(ReefRoleMixin):
    """Minimal host, standing in for an entity.

    The mixin reads two attributes it does not define, because on a real
    entity they come from Home Assistant's Entity base class. Declaring them
    here is what lets the mixin be exercised without dragging in an entity.
    """

    _attr_extra_state_attributes: dict[str, object] | None = None
    translation_key: str | None = None


def test_role_is_added_next_to_the_existing_attributes() -> None:
    obj = _Bare()
    obj._attr_extra_state_attributes = {"days_left": 3}
    obj.translation_key = "maint_pump_clean"
    assert obj.extra_state_attributes == {
        "days_left": 3,
        "reef_role": "maint_pump_clean",
    }


def test_role_alone_when_there_is_nothing_else() -> None:
    obj = _Bare()
    obj.translation_key = "maint_pump_clean"
    assert obj.extra_state_attributes == {"reef_role": "maint_pump_clean"}


def test_without_a_translation_key_the_attributes_pass_through() -> None:
    obj = _Bare()
    obj._attr_extra_state_attributes = {"days_left": 3}
    assert obj.extra_state_attributes == {"days_left": 3}


def test_nothing_at_all_yields_none() -> None:
    # None, not {}: Home Assistant skips the attribute dict entirely.
    assert _Bare().extra_state_attributes is None


def test_brand_device_id_is_prefixed() -> None:
    # It must never collide with an equipment id such as "tunze_1".
    assert brand_device_id("tunze") == "brand_tunze"


def test_library_task_translates_through_its_own_key() -> None:
    """A task without label is translated by HA under its own `maint_<task>` key."""
    from unittest.mock import MagicMock

    from custom_components.reef_maintenance.entity import ReefMaintenanceEntity
    from custom_components.reef_maintenance.storage import Equipment, TaskInstance
    from custom_components.reef_maintenance.tasks import MaintenanceTask

    task = MaintenanceTask("pump_clean", 14, 7, 90)
    equipment = Equipment("tunze_1", "Pump", "item:x", "Model")
    entity = ReefMaintenanceEntity(
        MagicMock(), "tunze", equipment, TaskInstance(task), "button", "_x"
    )
    assert entity._attr_translation_key == "maint_pump_clean_x"
    assert not hasattr(entity, "_attr_translation_placeholders") or (
        entity._attr_translation_placeholders in (None, {})
    )
