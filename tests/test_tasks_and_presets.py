"""Task library, preset composition and their invariants.

These are pure functions with no Home Assistant involved, so they are cheap
and they cover the part of the integration a mistake would be silent in: a
renamed task key loses the user's reset history, and a bad unit silently
changes what a slider means.
"""

from __future__ import annotations

import pytest

from custom_components.reef_maintenance.presets import (
    BRANDS,
    CUSTOM_PRESET,
    GENERIC_BRAND,
    PRESETS,
    Preset,
    TaskSpec,
    get_preset,
    presets_for_brand,
)
from custom_components.reef_maintenance.tasks import (
    CUSTOM_KEY,
    CUSTOM_TASK,
    DAYS_PER_UNIT,
    LIBRARY,
    ROLE_PREFIX,
    VALID_UNITS,
    custom_task,
    get_task,
    is_custom,
    translation_key_for,
)


class TestLibrary:
    def test_every_task_declares_a_known_unit(self) -> None:
        # An unknown unit falls back to 7 in the number entity, so a task
        # declared in days would silently be stored as weeks.
        for task in LIBRARY.values():
            assert task.unit in VALID_UNITS, task.key
            assert task.unit in DAYS_PER_UNIT, task.key

    def test_bounds_are_ordered_and_hold_the_default(self) -> None:
        for task in LIBRARY.values():
            assert task.min_days <= task.default_days <= task.max_days, task.key

    def test_bounds_survive_the_conversion_to_display_units(self) -> None:
        # The slider divides the day bounds by the unit factor; a min that
        # floors to zero would produce a slider starting at "0 weeks".
        for task in LIBRARY.values():
            factor = DAYS_PER_UNIT[task.unit]
            assert task.min_days // factor >= 1, task.key
            assert task.max_days // factor > task.min_days // factor, task.key

    def test_keys_match_their_dict_entry(self) -> None:
        # The dict is built from the tasks themselves; a mismatch would mean
        # get_task() returning a task whose key is not the one asked for.
        for key, task in LIBRARY.items():
            assert task.key == key

    def test_role_prefix_is_the_shared_contract(self) -> None:
        # ha-reef-card scans for this prefix; changing it silently empties
        # the maintenance view.
        assert ROLE_PREFIX == "maint_"
        for task in LIBRARY.values():
            assert task.translation_key == f"maint_{task.key}"

    def test_get_task_returns_none_for_an_unknown_key(self) -> None:
        assert get_task("pump_clean") is LIBRARY["pump_clean"]
        assert get_task("no_such_task") is None


class TestCustomTasks:
    def test_custom_task_keeps_the_slug_but_shares_the_translation(self) -> None:
        task = custom_task("filtre_a_charbon")
        assert task.key == f"{CUSTOM_KEY}_filtre_a_charbon"
        assert task.default_days == CUSTOM_TASK.default_days
        # All custom tasks share the generic keys: the label travels as a
        # translation placeholder instead.
        assert translation_key_for(task) == CUSTOM_TASK.translation_key

    def test_is_custom_recognises_both_forms(self) -> None:
        assert is_custom(CUSTOM_TASK)
        assert is_custom(custom_task("anything"))
        assert not is_custom(LIBRARY["pump_clean"])

    def test_library_task_keeps_its_own_translation_key(self) -> None:
        assert translation_key_for(LIBRARY["venturi_clean"]) == "maint_venturi_clean"


class TestPresets:
    def test_every_preset_references_existing_library_tasks(self) -> None:
        for preset in PRESETS.values():
            for spec in preset.tasks:
                assert spec.key in LIBRARY, f"{preset.id} -> {spec.key}"

    def test_every_preset_belongs_to_a_declared_brand(self) -> None:
        for preset in PRESETS.values():
            assert preset.brand in BRANDS, preset.id

    def test_resolve_applies_overrides_and_keeps_the_rest(self) -> None:
        spec = TaskSpec("pump_clean", default_days=60, min_days=40, max_days=100)
        resolved = spec.resolve()
        base = LIBRARY["pump_clean"]
        assert (resolved.default_days, resolved.min_days, resolved.max_days) == (
            60,
            40,
            100,
        )
        # Icon and unit are never overridden: they belong to the task, not to
        # the brand that uses it.
        assert resolved.icon == base.icon
        assert resolved.unit == base.unit

    def test_resolve_without_overrides_returns_the_library_values(self) -> None:
        resolved = TaskSpec("glass_clean").resolve()
        assert resolved == LIBRARY["glass_clean"]

    def test_presets_for_brand_filters_and_keeps_order(self) -> None:
        tunze = presets_for_brand("tunze")
        assert tunze
        assert all(p.brand == "tunze" for p in tunze)
        assert [p.id for p in tunze] == [
            p.id for p in PRESETS.values() if p.brand == "tunze"
        ]

    def test_unknown_brand_has_no_preset(self) -> None:
        assert presets_for_brand("no_such_brand") == []

    def test_custom_preset_preselects_nothing(self) -> None:
        preset = get_preset(CUSTOM_PRESET)
        assert preset is not None
        assert preset.brand == GENERIC_BRAND
        assert preset.tasks == ()

    def test_get_preset_returns_none_after_a_downgrade(self) -> None:
        # A preset removed from a later version must not raise on load.
        assert get_preset("removed_in_the_future") is None

    @pytest.mark.parametrize("preset", PRESETS.values(), ids=lambda p: p.id)
    def test_part_number_only_where_wear_parts_are_tracked(
        self, preset: Preset
    ) -> None:
        # The button surfaces part_number on the wear-parts task only, so a
        # reference on a preset without that task would never be shown.
        if preset.part_number is not None:
            assert any(spec.key == "wear_parts_replace" for spec in preset.tasks)
