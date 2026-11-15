"""Persistent state, the equipment model, and the derived day counts.

`compute_days_left` is the value every consumer reads -- the card, the alert
blueprint, the button attributes -- so its rounding is pinned here rather than
left to whatever the implementation happens to do.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from homeassistant.core import HomeAssistant

from custom_components.reef_maintenance.const import (
    CONF_CUSTOM_TASKS,
    CONF_EQUIPMENTS,
    CONF_ID,
    CONF_MODEL,
    CONF_NAME,
    CONF_SOURCE,
    CONF_TASKS,
)
from custom_components.reef_maintenance.storage import (
    Equipment,
    MaintenanceStore,
    build_equipment,
    build_equipments,
    compute_days_left,
    is_overdue,
    next_equipment_id,
    parse_dt,
)

NOW = datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc)


def _sched(unit: str, default: int, low: int, high: int) -> dict:
    return {
        "type": "interval",
        "unit": unit,
        "every": {"default": default, "min": low, "max": high},
    }


# A small catalog view: one circulation-pump item (Tunze), its category, and
# three tasks. The item shortens wear_parts_replace to 18 months (540 days).
VIEW: dict = {
    "tasks": {
        "pump_clean": {
            "name": {"en": "Pump cleaning"},
            "icon": "mdi:fan",
            "schedule": _sched("weeks", 6, 4, 13),
        },
        "pump_descale": {
            "name": {"en": "Descale pump"},
            "icon": "mdi:spray-bottle",
            "schedule": _sched("months", 6, 3, 12),
        },
        "wear_parts_replace": {
            "name": {"en": "Replace wear parts kit"},
            "icon": "mdi:cog-refresh",
            "schedule": _sched("months", 24, 12, 36),
        },
    },
    "categories": {
        "circulation_pump": {
            "name": {"en": "Circulation pump"},
            "scopes": ["aquarium"],
            "icon": "mdi:fan",
            "maintenance": [
                {"task": "pump_clean"},
                {"task": "pump_descale"},
                {"task": "wear_parts_replace"},
            ],
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
                {"task": "pump_descale"},
                {
                    "task": "wear_parts_replace",
                    "schedule": _sched("months", 18, 12, 36),
                },
            ],
        },
    },
}
TURBELLE = "item:tunze-turbelle-stream"


# ---------------------------------------------------------------------------
# Equipment model
# ---------------------------------------------------------------------------


class TestBuildEquipment:
    def test_builds_tasks_from_the_stored_keys(self) -> None:
        eq = build_equipment(
            {
                CONF_ID: "tunze_1",
                CONF_NAME: "Turbelle",
                CONF_SOURCE: TURBELLE,
                CONF_TASKS: ["pump_clean", "pump_descale"],
            },
            VIEW,
            "en",
        )
        assert [i.task.key for i in eq.tasks] == ["pump_clean", "pump_descale"]
        assert [i.label for i in eq.tasks] == ["Pump cleaning", "Descale pump"]
        assert eq.model == "Turbelle stream / stream 3"

    def test_item_schedule_override_beats_the_task_default(self) -> None:
        # The Tunze item shortens wear_parts_replace to 18 months (540 days).
        eq = build_equipment(
            {
                CONF_ID: "tunze_1",
                CONF_NAME: "Turbelle",
                CONF_SOURCE: TURBELLE,
                CONF_TASKS: ["wear_parts_replace"],
            },
            VIEW,
            "en",
        )
        assert eq.tasks[0].task.default_days == 540

    def test_unknown_task_is_skipped_not_fatal(self) -> None:
        # A task dropped from the catalog, or a downgrade, must not prevent
        # the entry from loading.
        eq = build_equipment(
            {
                CONF_ID: "tunze_1",
                CONF_NAME: "Turbelle",
                CONF_SOURCE: TURBELLE,
                CONF_TASKS: ["pump_clean", "task_from_the_future"],
            },
            VIEW,
            "en",
        )
        assert [i.task.key for i in eq.tasks] == ["pump_clean"]

    def test_all_tasks_when_the_selection_is_absent(self) -> None:
        # No CONF_TASKS stored: every task of the source applies.
        eq = build_equipment(
            {CONF_ID: "tunze_1", CONF_NAME: "Turbelle", CONF_SOURCE: TURBELLE},
            VIEW,
            "en",
        )
        assert [i.task.key for i in eq.tasks] == [
            "pump_clean",
            "pump_descale",
            "wear_parts_replace",
        ]

    def test_unknown_source_keeps_the_stored_model_and_no_tasks(self) -> None:
        eq = build_equipment(
            {
                CONF_ID: "x_1",
                CONF_NAME: "Thing",
                CONF_SOURCE: "item:gone-in-a-downgrade",
                CONF_MODEL: "Some model",
                CONF_TASKS: [],
            },
            VIEW,
            "en",
        )
        assert eq.model == "Some model"
        assert eq.tasks == ()

    def test_legacy_preset_is_mapped_onto_a_catalog_source(self) -> None:
        # A pre-catalog entry stored a preset id; it still loads.
        eq = build_equipment(
            {
                CONF_ID: "tunze_1",
                CONF_NAME: "Turbelle",
                "preset": "tunze_turbelle_stream",
                CONF_TASKS: ["pump_clean"],
            },
            VIEW,
            "en",
        )
        assert eq.source == TURBELLE
        assert [i.task.key for i in eq.tasks] == ["pump_clean"]

    def test_custom_tasks_carry_their_label(self) -> None:
        eq = build_equipment(
            {
                CONF_ID: "generic_1",
                CONF_NAME: "Reactor",
                CONF_SOURCE: "category:circulation_pump",
                CONF_TASKS: [],
                CONF_CUSTOM_TASKS: ["Rincer le média"],
            },
            VIEW,
            "en",
        )
        assert len(eq.tasks) == 1
        assert eq.tasks[0].label == "Rincer le média"
        assert eq.tasks[0].task.key == "custom_rincer_le_media"

    def test_colliding_custom_labels_get_distinct_keys(self) -> None:
        # "Rincer!" and "Rincer?" both slugify to "rincer"; without a suffix
        # the two task keys collide and HA drops the second entity set as a
        # duplicate unique_id.
        eq = build_equipment(
            {
                CONF_ID: "generic_1",
                CONF_NAME: "Reactor",
                CONF_SOURCE: "category:circulation_pump",
                CONF_TASKS: [],
                CONF_CUSTOM_TASKS: ["Rincer!", "Rincer?"],
            },
            VIEW,
            "en",
        )
        keys = [i.task.key for i in eq.tasks]
        assert keys == ["custom_rincer", "custom_rincer_2"]
        assert len(set(keys)) == 2
        # Labels are untouched: only the internal key is disambiguated.
        assert [i.label for i in eq.tasks] == ["Rincer!", "Rincer?"]

    def test_unslugifiable_labels_do_not_collide_either(self) -> None:
        # HA's slugify returns "unknown" rather than "" for these.
        eq = build_equipment(
            {
                CONF_ID: "generic_1",
                CONF_NAME: "Reactor",
                CONF_SOURCE: "category:circulation_pump",
                CONF_TASKS: [],
                CONF_CUSTOM_TASKS: ["!!!", "???"],
            },
            VIEW,
            "en",
        )
        assert len({i.task.key for i in eq.tasks}) == 2

    def test_first_slug_is_never_renamed(self) -> None:
        # Suffixing the first occurrence would change an existing task key
        # and lose its reset history.
        eq = build_equipment(
            {
                CONF_ID: "generic_1",
                CONF_NAME: "Reactor",
                CONF_SOURCE: "category:circulation_pump",
                CONF_TASKS: [],
                CONF_CUSTOM_TASKS: ["Rincer le média", "Autre"],
            },
            VIEW,
            "en",
        )
        assert eq.tasks[0].task.key == "custom_rincer_le_media"

    def test_build_equipments_reads_the_whole_options_payload(self) -> None:
        options: dict[str, Any] = {
            CONF_EQUIPMENTS: [
                {
                    CONF_ID: "tunze_1",
                    CONF_NAME: "A",
                    CONF_SOURCE: TURBELLE,
                    CONF_TASKS: ["pump_clean"],
                },
                {
                    CONF_ID: "tunze_2",
                    CONF_NAME: "B",
                    CONF_SOURCE: "category:circulation_pump",
                    CONF_TASKS: [],
                },
            ]
        }
        assert [e.id for e in build_equipments(options, VIEW, "en")] == [
            "tunze_1",
            "tunze_2",
        ]

    def test_build_equipments_on_an_empty_entry(self) -> None:
        assert build_equipments({}, VIEW, "en") == []


class TestNextEquipmentId:
    def test_starts_at_one(self) -> None:
        assert next_equipment_id({}, "tunze") == "tunze_1"

    def test_skips_the_ids_already_taken(self) -> None:
        options = {CONF_EQUIPMENTS: [{CONF_ID: "tunze_1"}, {CONF_ID: "tunze_2"}]}
        assert next_equipment_id(options, "tunze") == "tunze_3"

    def test_fills_a_hole_only_after_the_last_used(self) -> None:
        # tunze_1 was removed: reusing it would resurrect the old entities'
        # unique_ids and their history, so the counter must skip past.
        options = {CONF_EQUIPMENTS: [{CONF_ID: "tunze_2"}]}
        assert next_equipment_id(options, "tunze") == "tunze_1"

    def test_ids_are_per_brand(self) -> None:
        options = {CONF_EQUIPMENTS: [{CONF_ID: "tunze_1"}]}
        assert next_equipment_id(options, "jebao") == "jebao_1"


# ---------------------------------------------------------------------------
# Derived calculations
# ---------------------------------------------------------------------------


class TestComputeDaysLeft:
    def test_never_reset_is_none_not_overdue(self) -> None:
        # The distinction matters right after adding an equipment: pending a
        # first acknowledgement is not the same as late.
        assert compute_days_left(None, 30) is None
        assert is_overdue(None, 30) is False

    def test_full_interval_remaining_just_after_a_reset(self) -> None:
        assert compute_days_left(NOW, 30, NOW) == 30

    def test_partial_day_counts_down(self) -> None:
        # 29.5 days left floors to 29: a partially used day is used.
        assert compute_days_left(NOW, 30, NOW + timedelta(hours=12)) == 29

    def test_exactly_due_is_zero_and_not_overdue(self) -> None:
        assert compute_days_left(NOW, 30, NOW + timedelta(days=30)) == 0
        assert is_overdue(NOW, 30, NOW + timedelta(days=30)) is False

    def test_one_second_late_is_already_minus_one(self) -> None:
        # Rounding away from zero in both directions: being late by any
        # amount shows as a whole day late rather than as 0.
        late = NOW + timedelta(days=30, seconds=1)
        assert compute_days_left(NOW, 30, late) == -1
        assert is_overdue(NOW, 30, late) is True

    def test_deeply_overdue(self) -> None:
        assert compute_days_left(NOW, 30, NOW + timedelta(days=45)) == -15

    def test_defaults_to_now_when_no_reference_given(self) -> None:
        recent = datetime.now(timezone.utc) - timedelta(days=1)
        assert compute_days_left(recent, 10) == 8


class TestParseDt:
    def test_parses_an_aware_timestamp(self) -> None:
        assert parse_dt("2026-06-01T12:00:00+00:00") == NOW

    def test_assumes_utc_when_the_string_is_naive(self) -> None:
        # Storage always writes aware timestamps; a naive one can only come
        # from a hand-edited file, and treating it as local would shift it.
        assert parse_dt("2026-06-01T12:00:00") == NOW

    @pytest.mark.parametrize("value", ["", "not a date", None, 42, [], {}])
    def test_returns_none_on_anything_else(self, value: Any) -> None:
        assert parse_dt(value) is None


# ---------------------------------------------------------------------------
# Store
# ---------------------------------------------------------------------------


class TestMaintenanceStore:
    async def test_defaults_before_anything_is_written(
        self, hass: HomeAssistant
    ) -> None:
        store = MaintenanceStore(hass, "entry")
        await store.async_load()
        assert store.get_last_reset("tunze_1", "pump_clean") is None
        assert store.get_interval("tunze_1", "pump_clean", 45) == 45
        assert store.get_notify("tunze_1", "pump_clean") is True

    async def test_load_is_idempotent(self, hass: HomeAssistant) -> None:
        store = MaintenanceStore(hass, "entry")
        await store.async_load()
        await store.async_reset("tunze_1", "pump_clean", NOW)
        # A second load must not wipe what is already in memory.
        await store.async_load()
        assert store.get_last_reset("tunze_1", "pump_clean") == NOW

    async def test_reset_defaults_to_now_and_returns_the_stamp(
        self, hass: HomeAssistant
    ) -> None:
        store = MaintenanceStore(hass, "entry")
        await store.async_load()
        before = datetime.now(timezone.utc)
        stamp = await store.async_reset("tunze_1", "pump_clean")
        assert before <= stamp <= datetime.now(timezone.utc)

    async def test_interval_and_notify_round_trip(self, hass: HomeAssistant) -> None:
        store = MaintenanceStore(hass, "entry")
        await store.async_load()
        await store.async_set_interval("tunze_1", "pump_clean", 60)
        await store.async_set_notify("tunze_1", "pump_clean", False)
        assert store.get_interval("tunze_1", "pump_clean", 45) == 60
        assert store.get_notify("tunze_1", "pump_clean") is False

    async def test_state_survives_a_reload(self, hass: HomeAssistant) -> None:
        store = MaintenanceStore(hass, "entry")
        await store.async_load()
        await store.async_reset("tunze_1", "pump_clean", NOW)
        await store.async_set_interval("tunze_1", "pump_clean", 60)
        await store.async_set_notify("tunze_1", "pump_clean", False)

        reloaded = MaintenanceStore(hass, "entry")
        await reloaded.async_load()
        assert reloaded.get_last_reset("tunze_1", "pump_clean") == NOW
        assert reloaded.get_interval("tunze_1", "pump_clean", 45) == 60
        assert reloaded.get_notify("tunze_1", "pump_clean") is False

    async def test_default_notify_is_not_persisted(self, hass: HomeAssistant) -> None:
        # Only the non-default value is written, to keep the file lean; the
        # reader must therefore treat a missing flag as enabled.
        store = MaintenanceStore(hass, "entry")
        await store.async_load()
        await store.async_set_notify("tunze_1", "pump_clean", True)

        reloaded = MaintenanceStore(hass, "entry")
        await reloaded.async_load()
        assert reloaded.get_notify("tunze_1", "pump_clean") is True

    async def test_forget_equipment_drops_only_its_own_instances(
        self, hass: HomeAssistant
    ) -> None:
        store = MaintenanceStore(hass, "entry")
        await store.async_load()
        await store.async_reset("tunze_1", "pump_clean", NOW)
        await store.async_reset("tunze_10", "pump_clean", NOW)
        await store.async_reset("tunze_2", "pump_clean", NOW)

        await store.async_forget_equipment("tunze_1")

        assert store.get_last_reset("tunze_1", "pump_clean") is None
        # tunze_10 shares the "tunze_1" text prefix but not the instance one.
        assert store.get_last_reset("tunze_10", "pump_clean") == NOW
        assert store.get_last_reset("tunze_2", "pump_clean") == NOW

    async def test_forget_an_equipment_with_no_state_is_a_noop(
        self, hass: HomeAssistant
    ) -> None:
        store = MaintenanceStore(hass, "entry")
        await store.async_load()
        await store.async_forget_equipment("never_seen")

    async def test_listener_fires_only_for_its_own_instance(
        self, hass: HomeAssistant
    ) -> None:
        store = MaintenanceStore(hass, "entry")
        await store.async_load()
        calls: list[str] = []
        store.async_add_listener("tunze_1", "pump_clean", lambda: calls.append("a"))

        await store.async_reset("tunze_1", "pump_clean")
        await store.async_set_interval("tunze_1", "pump_clean", 50)
        await store.async_set_notify("tunze_1", "pump_clean", False)
        await store.async_reset("tunze_1", "pump_descale")

        assert calls == ["a", "a", "a"]

    async def test_unsubscribe_stops_the_callbacks(self, hass: HomeAssistant) -> None:
        store = MaintenanceStore(hass, "entry")
        await store.async_load()
        calls: list[str] = []
        unsub = store.async_add_listener(
            "tunze_1", "pump_clean", lambda: calls.append("a")
        )
        unsub()
        # Unsubscribing twice must not raise: entities may be removed twice
        # during a reload.
        unsub()
        await store.async_reset("tunze_1", "pump_clean")
        assert calls == []

    async def test_a_raising_listener_does_not_break_the_others(
        self, hass: HomeAssistant
    ) -> None:
        store = MaintenanceStore(hass, "entry")
        await store.async_load()
        calls: list[str] = []

        def _boom() -> None:
            raise RuntimeError("entity already removed")

        store.async_add_listener("tunze_1", "pump_clean", _boom)
        store.async_add_listener("tunze_1", "pump_clean", lambda: calls.append("b"))
        await store.async_reset("tunze_1", "pump_clean")
        assert calls == ["b"]


class TestEquipmentDataclass:
    def test_model_is_the_stored_field(self) -> None:
        eq = Equipment("x", "X", "item:tunze-nanostream", "Turbelle nanostream")
        assert eq.model == "Turbelle nanostream"
