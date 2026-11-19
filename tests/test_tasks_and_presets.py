"""Task model and catalog resolution — pure functions, no Home Assistant.

These cover the parts a mistake would be silent in: a renamed task key loses
the user's reset history, a bad unit silently changes what a slider means, and
a wrong schedule conversion changes an interval by weeks.
"""

from __future__ import annotations

from custom_components.reef_maintenance.catalog import (
    CATEGORY,
    GENERIC_BRAND,
    ITEM,
    LEGACY_PRESETS,
    brands,
    choices,
    localize,
    model_label,
    resolve_equipment_tasks,
    split_source,
)
from custom_components.reef_maintenance.tasks import (
    CUSTOM_KEY,
    CUSTOM_TASK,
    DAYS_PER_UNIT,
    ROLE_PREFIX,
    VALID_UNITS,
    custom_task,
)


def _sched(unit: str, default: int, low: int, high: int) -> dict:
    return {
        "type": "interval",
        "unit": unit,
        "every": {"default": default, "min": low, "max": high},
    }


VIEW: dict = {
    "tasks": {
        "pump_clean": {
            "name": {"en": "Pump cleaning", "fr": "Nettoyage de la pompe"},
            "icon": "mdi:fan",
            "schedule": _sched("weeks", 6, 4, 13),
        },
        "wear_parts_replace": {
            "name": {"en": "Replace wear parts kit"},
            "icon": "mdi:cog-refresh",
            "schedule": _sched("months", 24, 12, 36),
        },
    },
    "categories": {
        "circulation_pump": {
            "name": {"en": "Circulation pump", "fr": "Pompe de brassage"},
            "scopes": ["aquarium"],
            "icon": "mdi:fan",
            "maintenance": [{"task": "pump_clean"}, {"task": "wear_parts_replace"}],
        },
    },
    "items": {
        "tunze-turbelle-stream": {
            "category": "circulation_pump",
            "brand": "Tunze",
            "model": "Turbelle stream / stream 3",
            "inherit_maintenance": False,
            "maintenance": [
                {"task": "pump_clean"},
                {
                    "task": "wear_parts_replace",
                    "schedule": _sched("months", 18, 12, 36),
                },
            ],
        },
    },
}
TURBELLE = "item:tunze-turbelle-stream"


class TestTaskModel:
    def test_role_prefix_is_the_shared_contract(self) -> None:
        # ha-reef-card scans for this prefix; changing it silently empties the
        # maintenance view.
        assert ROLE_PREFIX == "maint_"

    def test_translation_key_is_the_reef_role(self) -> None:
        assert custom_task("x").translation_key.startswith("maint_")

    def test_valid_units_are_all_convertible(self) -> None:
        for unit in VALID_UNITS:
            assert unit in DAYS_PER_UNIT


class TestCustomTask:
    def test_custom_task_keeps_the_slug_and_shares_the_bounds(self) -> None:
        task = custom_task("filtre_a_charbon")
        assert task.key == f"{CUSTOM_KEY}_filtre_a_charbon"
        assert task.default_days == CUSTOM_TASK.default_days
        assert task.unit == CUSTOM_TASK.unit


class TestCatalogResolution:
    def test_schedule_is_converted_to_days(self) -> None:
        resolved = resolve_equipment_tasks(VIEW, TURBELLE, "en")
        pump = resolved["pump_clean"][0]
        # 6/4/13 weeks -> 42/28/91 days, display unit kept.
        assert (pump.default_days, pump.min_days, pump.max_days) == (42, 28, 91)
        assert pump.unit == "weeks"
        assert pump.icon == "mdi:fan"

    def test_item_schedule_override_wins(self) -> None:
        resolved = resolve_equipment_tasks(VIEW, TURBELLE, "en")
        wear = resolved["wear_parts_replace"][0]
        # 18 months override -> 540 days (the task default is 24 months).
        assert wear.default_days == 540

    def test_task_name_is_localized_with_fallback(self) -> None:
        assert resolve_equipment_tasks(VIEW, TURBELLE, "fr")["pump_clean"][1] == (
            "Nettoyage de la pompe"
        )
        # wear_parts has no French name: falls back to English.
        assert (
            resolve_equipment_tasks(VIEW, TURBELLE, "fr")["wear_parts_replace"][1]
            == "Replace wear parts kit"
        )

    def test_a_category_resolves_its_own_tasks(self) -> None:
        resolved = resolve_equipment_tasks(VIEW, "category:circulation_pump", "en")
        assert set(resolved) == {"pump_clean", "wear_parts_replace"}

    def test_unknown_source_resolves_to_nothing(self) -> None:
        assert resolve_equipment_tasks(VIEW, "item:nope", "en") == {}


class TestBrandsAndChoices:
    def test_brands_are_the_generic_kind_plus_item_brands(self) -> None:
        assert brands(VIEW) == {GENERIC_BRAND: "Other / generic", "tunze": "Tunze"}

    def test_choices_for_a_brand_are_its_items(self) -> None:
        assert choices(VIEW, "tunze", "en") == [
            (TURBELLE, "Turbelle stream / stream 3")
        ]

    def test_choices_for_the_generic_brand_are_categories(self) -> None:
        assert choices(VIEW, GENERIC_BRAND, "fr") == [
            ("category:circulation_pump", "Pompe de brassage")
        ]


class TestSourceHelpers:
    def test_split_source_reads_the_prefix(self) -> None:
        assert split_source(f"{ITEM}x") == ("x", None)
        assert split_source(f"{CATEGORY}y") == (None, "y")
        assert split_source("garbage") == (None, None)

    def test_model_label_of_an_item_and_a_category(self) -> None:
        assert model_label(VIEW, TURBELLE, "en") == "Turbelle stream / stream 3"
        assert (
            model_label(VIEW, "category:circulation_pump", "fr") == "Pompe de brassage"
        )

    def test_model_label_of_an_unknown_source_is_its_id(self) -> None:
        assert model_label(VIEW, "item:ghost", "en") == "ghost"

    def test_localize_falls_back_then_gives_up(self) -> None:
        assert localize({"en": "E"}, "fr") == "E"
        assert localize({"pl": "P"}, "fr") == "P"
        assert localize(None, "fr") is None


class TestLegacyPresets:
    def test_retired_presets_map_onto_catalog_sources(self) -> None:
        assert LEGACY_PRESETS["tunze_turbelle_stream"] == TURBELLE
        assert LEGACY_PRESETS["generic_heater"] == f"{CATEGORY}heater"
        # Every mapping points at an item or a category.
        for target in LEGACY_PRESETS.values():
            assert target.startswith((ITEM, CATEGORY))


def test_unknown_catalog_unit_falls_back_to_weeks() -> None:
    """A schedule unit the integration does not know is read as weeks."""
    from custom_components.reef_maintenance.catalog import _task_from_catalog

    task = _task_from_catalog(
        {"task": "x", "schedule": {"unit": "decades", "every": {"default": 2}}}
    )
    assert task.unit == "weeks"
    assert task.default_days == 14
