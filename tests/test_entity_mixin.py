"""The ReefRoleMixin on its own.

The mixin is the shared contract with ha-reefbeat-component and
ha-aquamedic-component, and its fallback paths are unreachable from the four
real entities (they all set a translation_key), so they are exercised here
directly rather than left untested.
"""

from __future__ import annotations

from custom_components.reef_maintenance.entity import ReefRoleMixin, brand_device_id


class _Bare(ReefRoleMixin):
    """Minimal host, standing in for an entity."""


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
