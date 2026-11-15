"""The four entities of a task: button, number, switch and date."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util

from custom_components.reef_maintenance.const import CONF_EQUIPMENTS, DOMAIN


def entity_of(hass: HomeAssistant, entry, domain: str, task: str) -> str:
    """Return the entity_id of one platform for one task."""
    return next(
        e.entity_id
        for e in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
        if e.domain == domain and f"_{task}_" in f"{e.unique_id}_"
    )


def state_of(hass: HomeAssistant, entity_id: str) -> State:
    """Return a state, failing clearly when the entity was never created.

    `hass.states.get` is Optional; asserting here turns a downstream
    `AttributeError: 'NoneType' has no attribute 'attributes'` into a failure
    naming the entity that is missing.
    """
    state = hass.states.get(entity_id)
    assert state is not None, f"no state for {entity_id}"
    return state


class TestButton:
    async def test_attributes_before_any_reset(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        state = state_of(hass, entity_of(hass, loaded_entry, "button", "pump_clean"))
        assert state.attributes["reef_role"] == "maint_pump_clean"
        assert state.attributes["task_key"] == "pump_clean"
        # The Tunze item runs pump_clean every ~6 weeks (45 days -> 6 weeks).
        assert state.attributes["interval_days"] == 42
        assert state.attributes["last_reset"] is None
        # Never reset is not overdue: the task awaits a first acknowledgement.
        assert state.attributes["days_left"] is None
        assert state.attributes["overdue"] is False
        assert state.attributes["notify"] is True

    async def test_press_records_the_reset_and_refreshes(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        entity_id = entity_of(hass, loaded_entry, "button", "pump_clean")
        await hass.services.async_call(
            "button", "press", {"entity_id": entity_id}, blocking=True
        )
        await hass.async_block_till_done()

        state = state_of(hass, entity_id)
        assert state.attributes["last_reset"] is not None
        # 41, not 42: the microseconds elapsed since the press already make
        # this a partially used day, and a partial day counts.
        assert state.attributes["days_left"] == 41
        assert state.attributes["overdue"] is False

    async def test_overdue_is_reported(self, hass: HomeAssistant, loaded_entry) -> None:
        store = hass.data[DOMAIN][loaded_entry.entry_id]["store"]
        await store.async_reset(
            "tunze_1", "pump_clean", datetime.now(timezone.utc) - timedelta(days=50)
        )
        await hass.async_block_till_done()

        state = state_of(hass, entity_of(hass, loaded_entry, "button", "pump_clean"))
        assert state.attributes["days_left"] == -8
        assert state.attributes["overdue"] is True

    async def test_icon_comes_from_the_task(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        state = state_of(hass, entity_of(hass, loaded_entry, "button", "pump_clean"))
        assert state.attributes["icon"] == "mdi:pump"


class TestIntervalNumber:
    async def test_value_is_shown_in_the_task_unit(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        # The Tunze item runs pump_clean every 6 weeks (4-13).
        state = state_of(hass, entity_of(hass, loaded_entry, "number", "pump_clean"))
        assert float(state.state) == 6.0
        assert state.attributes["min"] == 4.0
        assert state.attributes["max"] == 13.0

    async def test_unit_travels_in_the_role(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        # This is how ha-reef-card knows what the number means without an
        # extra attribute.
        state = state_of(hass, entity_of(hass, loaded_entry, "number", "pump_clean"))
        assert state.attributes["reef_role"] == "maint_pump_clean_interval_weeks"

    async def test_setting_the_value_converts_back_to_days(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        entity_id = entity_of(hass, loaded_entry, "number", "pump_clean")
        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": entity_id, "value": 8},
            blocking=True,
        )
        store = hass.data[DOMAIN][loaded_entry.entry_id]["store"]
        assert store.get_interval("tunze_1", "pump_clean", 45) == 56

    async def test_a_task_declared_in_days_is_not_divided(
        self, hass: HomeAssistant, entry_factory, make_equipment, setup
    ) -> None:
        # "days" has to be listed in DAYS_PER_UNIT, otherwise the fallback
        # factor of 7 would silently turn 7 days into 1. The aquarium category
        # runs glass_clean every 7 days.
        entry = await setup(
            hass,
            entry_factory(
                brand="generic",
                equipments=[
                    make_equipment(
                        "generic_1",
                        "Tank",
                        "category:aquarium",
                        "Aquarium (routine)",
                        ["glass_clean"],
                    )
                ],
            ),
        )
        state = state_of(hass, entity_of(hass, entry, "number", "glass_clean"))
        assert float(state.state) == 7.0
        assert state.attributes["reef_role"] == "maint_glass_clean_interval_days"

    async def test_a_task_declared_in_months(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        # wear_parts_replace on the Tunze item: ~24 months.
        state = state_of(
            hass, entity_of(hass, loaded_entry, "number", "wear_parts_replace")
        )
        assert float(state.state) == 24.0


class TestNotifySwitch:
    async def test_defaults_to_enabled(self, hass: HomeAssistant, loaded_entry) -> None:
        state = state_of(hass, entity_of(hass, loaded_entry, "switch", "pump_clean"))
        assert state.state == "on"
        assert state.attributes["icon"] == "mdi:bell-ring"

    async def test_turning_off_persists_and_flips_the_icon(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        entity_id = entity_of(hass, loaded_entry, "switch", "pump_clean")
        await hass.services.async_call(
            "switch", "turn_off", {"entity_id": entity_id}, blocking=True
        )
        await hass.async_block_till_done()

        state = state_of(hass, entity_id)
        assert state.state == "off"
        assert state.attributes["icon"] == "mdi:bell-off"

        store = hass.data[DOMAIN][loaded_entry.entry_id]["store"]
        assert store.get_notify("tunze_1", "pump_clean") is False

    async def test_turning_back_on(self, hass: HomeAssistant, loaded_entry) -> None:
        entity_id = entity_of(hass, loaded_entry, "switch", "pump_clean")
        await hass.services.async_call(
            "switch", "turn_off", {"entity_id": entity_id}, blocking=True
        )
        await hass.services.async_call(
            "switch", "turn_on", {"entity_id": entity_id}, blocking=True
        )
        await hass.async_block_till_done()
        assert state_of(hass, entity_id).state == "on"

    async def test_a_muted_task_reads_muted_on_reload(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        # The switch reads the store before its first state is written, else
        # a muted task would flash as enabled after every restart.
        store = hass.data[DOMAIN][loaded_entry.entry_id]["store"]
        await store.async_set_notify("tunze_1", "pump_clean", False)

        await hass.config_entries.async_reload(loaded_entry.entry_id)
        await hass.async_block_till_done()

        state = state_of(hass, entity_of(hass, loaded_entry, "switch", "pump_clean"))
        assert state.state == "off"

    async def test_the_switch_is_mirrored_in_the_button_attributes(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        # So the alert blueprint never has to correlate two entities.
        await hass.services.async_call(
            "switch",
            "turn_off",
            {"entity_id": entity_of(hass, loaded_entry, "switch", "pump_clean")},
            blocking=True,
        )
        await hass.async_block_till_done()
        button = state_of(hass, entity_of(hass, loaded_entry, "button", "pump_clean"))
        assert button.attributes["notify"] is False


class TestLastResetDate:
    async def test_empty_until_the_first_reset(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        state = state_of(hass, entity_of(hass, loaded_entry, "date", "pump_clean"))
        assert state.state == "unknown"

    async def test_shows_the_stored_reset_in_local_time(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        # Stored in UTC: a late-evening reset must not display as the day
        # after in the user's timezone.
        store = hass.data[DOMAIN][loaded_entry.entry_id]["store"]
        stamp = datetime(2026, 3, 10, 22, 30, tzinfo=timezone.utc)
        await store.async_reset("tunze_1", "pump_clean", stamp)
        await hass.async_block_till_done()

        state = state_of(hass, entity_of(hass, loaded_entry, "date", "pump_clean"))
        assert state.state == dt_util.as_local(stamp).date().isoformat()

    async def test_setting_a_date_backdates_the_task(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        entity_id = entity_of(hass, loaded_entry, "date", "pump_clean")
        await hass.services.async_call(
            "date",
            "set_value",
            {"entity_id": entity_id, "date": "2026-03-01"},
            blocking=True,
        )
        await hass.async_block_till_done()

        store = hass.data[DOMAIN][loaded_entry.entry_id]["store"]
        stored = store.get_last_reset("tunze_1", "pump_clean")
        # Anchored at local midnight, so "3 days ago" means the same to the
        # user and to days_left.
        assert dt_util.as_local(stored).date() == date(2026, 3, 1)
        assert dt_util.as_local(stored).hour == 0


class TestCustomTaskEntities:
    async def test_a_custom_task_gets_its_four_entities(
        self, hass: HomeAssistant, entry_factory, make_equipment, setup
    ) -> None:
        entry = await setup(
            hass,
            entry_factory(
                brand="generic",
                equipments=[
                    make_equipment(
                        "generic_1",
                        "Reactor",
                        "custom",
                        tasks=[],
                        custom_tasks=["Rincer le média"],
                    )
                ],
            ),
        )
        entities = [
            e
            for e in er.async_entries_for_config_entry(
                er.async_get(hass), entry.entry_id
            )
            if not e.unique_id.startswith("catalog_")
        ]
        assert len(entities) == 4

    async def test_custom_tasks_keep_a_task_specific_role(
        self, hass: HomeAssistant, entry_factory, make_equipment, setup
    ) -> None:
        # The label is a translation placeholder (not a translation key), but
        # the role stays task-specific so ha-reef-card can tell tasks apart.
        entry = await setup(
            hass,
            entry_factory(
                brand="generic",
                equipments=[
                    make_equipment(
                        "generic_1",
                        "Reactor",
                        "custom",
                        tasks=[],
                        custom_tasks=["Rincer le média"],
                    )
                ],
            ),
        )
        button = next(
            e
            for e in er.async_entries_for_config_entry(
                er.async_get(hass), entry.entry_id
            )
            if e.domain == "button"
        )
        state = state_of(hass, button.entity_id)
        assert state.attributes["reef_role"] == "maint_custom_rincer_le_media"
        assert state.attributes["task_key"] == "custom_rincer_le_media"


class TestEntityLifecycle:
    async def test_entities_stop_listening_once_removed(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        # A stale listener writing state on a removed entity raises inside
        # the store's notify loop.
        store = hass.data[DOMAIN][loaded_entry.entry_id]["store"]
        hass.config_entries.async_update_entry(
            loaded_entry, options={CONF_EQUIPMENTS: []}
        )
        await hass.async_block_till_done()
        await store.async_reset("tunze_1", "pump_clean")
        await hass.async_block_till_done()
