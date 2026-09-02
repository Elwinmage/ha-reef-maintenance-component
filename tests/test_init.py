"""Entry setup, unload, device removal and the reset service."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from custom_components.reef_maintenance import async_remove_config_entry_device
from custom_components.reef_maintenance.const import (
    ATTR_LAST_RESET,
    CONF_EQUIPMENTS,
    DOMAIN,
    SERVICE_RESET,
)
from custom_components.reef_maintenance.entity import brand_device_id


def device_of(hass: HomeAssistant, identifier: str) -> dr.DeviceEntry:
    """Return a device, failing clearly when it was never registered.

    Iterates the device registry directly — the mapping-style and
    identifier-based lookups are deprecated or require a config_entry_id.
    """
    registry = dr.async_get(hass)
    for dev in registry.devices:
        if (DOMAIN, identifier) in dev.identifiers:
            return dev
    raise AssertionError(f"no device registered for {identifier}")


class TestSetup:
    async def test_entry_loads_and_registers_the_brand_device(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        assert loaded_entry.state is ConfigEntryState.LOADED

        device = device_of(hass, brand_device_id("tunze"))
        assert device.manufacturer == "Tunze"
        # A service device: it is the entry, not a piece of gear.
        assert device.entry_type is dr.DeviceEntryType.SERVICE

    async def test_equipment_is_a_device_under_the_brand(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        brand = device_of(hass, brand_device_id("tunze"))
        eq = device_of(hass, "tunze_1")
        assert eq.name == "Turbelle 6095"
        # via_device is what groups the pumps under the brand instead of
        # listing them flat.
        assert eq.via_device_id == brand.id

    async def test_four_entities_per_task(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        entities = er.async_entries_for_config_entry(
            er.async_get(hass), loaded_entry.entry_id
        )
        # Two tasks x (button, number, switch, date).
        assert len(entities) == 8
        domains = sorted({e.domain for e in entities})
        assert domains == ["button", "date", "number", "switch"]

    async def test_every_task_entity_publishes_reef_role(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        # The shared contract: ha-reef-card scans for this attribute.
        states = [
            hass.states.get(e.entity_id)
            for e in er.async_entries_for_config_entry(
                er.async_get(hass), loaded_entry.entry_id
            )
        ]
        roles = [s.attributes.get("reef_role") for s in states if s]
        assert all(r and r.startswith("maint_") for r in roles), roles

    async def test_unload_releases_the_entry_data(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        assert await hass.config_entries.async_unload(loaded_entry.entry_id)
        await hass.async_block_till_done()
        assert loaded_entry.state is ConfigEntryState.NOT_LOADED
        assert loaded_entry.entry_id not in hass.data.get(DOMAIN, {})

    async def test_an_entry_with_no_equipment_still_loads(
        self, hass: HomeAssistant, entry_factory, setup
    ) -> None:
        # This is the state right after adding the integration, before the
        # first equipment is created.
        entry = await setup(hass, entry_factory(equipments=[]))
        assert entry.state is ConfigEntryState.LOADED
        assert (
            er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id) == []
        )

    async def test_changing_the_options_reloads_the_entry(
        self, hass: HomeAssistant, loaded_entry, make_equipment
    ) -> None:
        # The entity set follows the equipment list, so options changes must
        # reload rather than be applied in place.
        hass.config_entries.async_update_entry(
            loaded_entry,
            options={
                CONF_EQUIPMENTS: [
                    make_equipment(),
                    make_equipment(
                        "tunze_2", "Nanostream", "tunze_nanostream", ["pump_clean"]
                    ),
                ]
            },
        )
        await hass.async_block_till_done()
        entities = er.async_entries_for_config_entry(
            er.async_get(hass), loaded_entry.entry_id
        )
        assert len(entities) == 12


class TestRemoveDevice:
    async def test_removing_an_equipment_drops_it_from_the_options(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        device = device_of(hass, "tunze_1")
        assert await async_remove_config_entry_device(hass, loaded_entry, device)
        await hass.async_block_till_done()
        assert loaded_entry.options[CONF_EQUIPMENTS] == []

    async def test_the_brand_device_is_not_removable(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        # It represents the entry itself; deleting it from the device page
        # would leave an entry with no device.
        device = device_of(hass, brand_device_id("tunze"))
        assert not await async_remove_config_entry_device(hass, loaded_entry, device)

    async def test_a_foreign_device_is_refused(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        registry = dr.async_get(hass)
        other = registry.async_get_or_create(
            config_entry_id=loaded_entry.entry_id,
            identifiers={("other_domain", "whatever")},
        )
        assert not await async_remove_config_entry_device(hass, loaded_entry, other)

    async def test_removal_forgets_the_stored_history(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        store = hass.data[DOMAIN][loaded_entry.entry_id]["store"]
        await store.async_reset("tunze_1", "pump_clean")
        assert store.get_last_reset("tunze_1", "pump_clean") is not None

        device = device_of(hass, "tunze_1")
        await async_remove_config_entry_device(hass, loaded_entry, device)
        assert store.get_last_reset("tunze_1", "pump_clean") is None


class TestResetService:
    async def test_service_is_registered_once(
        self, hass: HomeAssistant, loaded_entry, entry_factory, setup
    ) -> None:
        assert hass.services.has_service(DOMAIN, SERVICE_RESET)
        # A second entry must not fail on a duplicate registration.
        await setup(
            hass, entry_factory(brand="jebao", equipments=[], entry_id="second")
        )
        assert hass.services.has_service(DOMAIN, SERVICE_RESET)

    async def _button_of(self, hass: HomeAssistant, entry) -> str:
        entities = er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
        return next(
            e.entity_id
            for e in entities
            if e.domain == "button" and "pump_clean" in e.unique_id
        )

    async def test_reset_stamps_the_task(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        entity_id = await self._button_of(hass, loaded_entry)
        await hass.services.async_call(
            DOMAIN, SERVICE_RESET, {"entity_id": entity_id}, blocking=True
        )
        store = hass.data[DOMAIN][loaded_entry.entry_id]["store"]
        assert store.get_last_reset("tunze_1", "pump_clean") is not None

    async def test_reset_accepts_an_explicit_date(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        entity_id = await self._button_of(hass, loaded_entry)
        when = datetime(2026, 1, 15, 8, 0, tzinfo=timezone.utc)
        await hass.services.async_call(
            DOMAIN,
            SERVICE_RESET,
            {"entity_id": entity_id, ATTR_LAST_RESET: when.isoformat()},
            blocking=True,
        )
        store = hass.data[DOMAIN][loaded_entry.entry_id]["store"]
        assert store.get_last_reset("tunze_1", "pump_clean") == when

    async def test_any_of_the_four_entities_resolves_to_the_same_task(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        # The number entity is not the "action" one, but it identifies the
        # same instance; accepting only the button would surprise users.
        entities = er.async_entries_for_config_entry(
            er.async_get(hass), loaded_entry.entry_id
        )
        number = next(
            e.entity_id
            for e in entities
            if e.domain == "number" and "pump_clean" in e.unique_id
        )
        await hass.services.async_call(
            DOMAIN, SERVICE_RESET, {"entity_id": number}, blocking=True
        )
        store = hass.data[DOMAIN][loaded_entry.entry_id]["store"]
        assert store.get_last_reset("tunze_1", "pump_clean") is not None

    async def test_an_unknown_entity_is_ignored_not_fatal(
        self, hass: HomeAssistant, loaded_entry, caplog: pytest.LogCaptureFixture
    ) -> None:
        # An NFC tag pointing at a renamed entity must not break the whole
        # service call.
        await hass.services.async_call(
            DOMAIN,
            SERVICE_RESET,
            {"entity_id": "button.does_not_exist"},
            blocking=True,
        )
        assert "not a reef_maintenance task entity" in caplog.text

    async def test_an_entity_of_another_integration_is_ignored(
        self, hass: HomeAssistant, loaded_entry, caplog: pytest.LogCaptureFixture
    ) -> None:
        registry = er.async_get(hass)
        foreign = registry.async_get_or_create(
            "button", "other_domain", "unique", suggested_object_id="foreign"
        )
        await hass.services.async_call(
            DOMAIN, SERVICE_RESET, {"entity_id": foreign.entity_id}, blocking=True
        )
        assert "not a reef_maintenance task entity" in caplog.text


class TestResolveInstanceEdgeCases:
    async def test_an_entity_whose_entry_is_unloaded_is_ignored(
        self, hass: HomeAssistant, loaded_entry, caplog
    ) -> None:
        # The registry outlives the entry data: a service call during a
        # reload must not raise on the missing hass.data slot.
        entity_id = next(
            e.entity_id
            for e in er.async_entries_for_config_entry(
                er.async_get(hass), loaded_entry.entry_id
            )
            if e.domain == "button"
        )
        hass.data[DOMAIN].pop(loaded_entry.entry_id)
        await hass.services.async_call(
            DOMAIN, SERVICE_RESET, {"entity_id": entity_id}, blocking=True
        )
        assert "not a reef_maintenance task entity" in caplog.text

    async def test_an_orphan_unique_id_is_ignored(
        self, hass: HomeAssistant, loaded_entry, caplog
    ) -> None:
        # An entity left over from an equipment that no longer exists in the
        # options: no instance matches its unique_id prefix.
        registry = er.async_get(hass)
        orphan = registry.async_get_or_create(
            "button",
            DOMAIN,
            "tunze_9_pump_clean_action",
            config_entry=loaded_entry,
            suggested_object_id="orphan",
        )
        await hass.services.async_call(
            DOMAIN, SERVICE_RESET, {"entity_id": orphan.entity_id}, blocking=True
        )
        assert "not a reef_maintenance task entity" in caplog.text
