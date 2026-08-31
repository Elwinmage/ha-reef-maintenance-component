"""Config flow (one entry per brand) and options flow (the equipments)."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.reef_maintenance.const import (
    CONF_BRAND,
    CONF_CUSTOM_TASKS,
    CONF_EQUIPMENTS,
    CONF_ID,
    CONF_NAME,
    CONF_PRESET,
    CONF_TASKS,
    DOMAIN,
)


def schema_default(result: Any, key: str) -> Any:
    """Return the default a form proposes for one field.

    `data_schema` is Optional on a flow result, so this asserts rather than
    letting the test die on an unhelpful `NoneType has no attribute schema`.
    """
    schema = result["data_schema"]
    assert schema is not None, f"step {result.get('step_id')} has no schema"
    return next(marker.default() for marker in schema.schema if str(marker) == key)


class TestConfigFlow:
    async def test_creates_one_entry_per_brand(self, hass: HomeAssistant) -> None:
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_BRAND: "tunze"}
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert result["title"] == "Tunze"
        assert result["data"] == {CONF_BRAND: "tunze"}
        # The equipment list starts empty and is filled from the options.
        assert result["options"] == {CONF_EQUIPMENTS: []}

    async def test_the_same_brand_cannot_be_added_twice(
        self, hass: HomeAssistant
    ) -> None:
        # Equipment ids are `<brand>_<n>`, so a second Tunze entry would
        # hand out ids that collide with the first.
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_BRAND: "tunze"}
        )

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_BRAND: "tunze"}
        )
        assert result["type"] is FlowResultType.ABORT
        assert result["reason"] == "already_configured"

    async def test_another_brand_is_accepted(self, hass: HomeAssistant) -> None:
        for brand in ("tunze", "jebao"):
            result = await hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_USER}
            )
            result = await hass.config_entries.flow.async_configure(
                result["flow_id"], {CONF_BRAND: brand}
            )
            assert result["type"] is FlowResultType.CREATE_ENTRY


class TestOptionsFlowAdd:
    async def test_menu_offers_only_add_when_empty(
        self, hass: HomeAssistant, entry_factory, setup
    ) -> None:
        entry = await setup(hass, entry_factory(equipments=[]))
        result = await hass.config_entries.options.async_init(entry.entry_id)
        assert result["type"] is FlowResultType.MENU
        assert result["menu_options"] == ["add"]

    async def test_menu_offers_edit_and_remove_once_populated(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        result = await hass.config_entries.options.async_init(loaded_entry.entry_id)
        assert result["menu_options"] == ["add", "edit", "remove"]

    async def test_adding_preselects_the_preset_tasks(
        self, hass: HomeAssistant, entry_factory, setup
    ) -> None:
        entry = await setup(hass, entry_factory(equipments=[]))
        result = await hass.config_entries.options.async_init(entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": "add"}
        )
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {CONF_NAME: "Turbelle", CONF_PRESET: "tunze_turbelle_stream"},
        )
        assert result["step_id"] == "tasks"

        # Preselected, not imposed: the user may untick any of them.
        assert schema_default(result, CONF_TASKS) == [
            "pump_clean",
            "magnet_holder_clean",
            "pump_descale",
            "wear_parts_replace",
        ]

    async def test_adding_writes_the_equipment_with_a_fresh_id(
        self, hass: HomeAssistant, entry_factory, setup
    ) -> None:
        entry = await setup(hass, entry_factory(equipments=[]))
        result = await hass.config_entries.options.async_init(entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": "add"}
        )
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {CONF_NAME: "Turbelle", CONF_PRESET: "tunze_turbelle_stream"},
        )
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {CONF_TASKS: ["pump_clean"], CONF_CUSTOM_TASKS: ["Graisser"]},
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY

        await hass.async_block_till_done()
        equipments = entry.options[CONF_EQUIPMENTS]
        assert len(equipments) == 1
        assert equipments[0][CONF_ID] == "tunze_1"
        assert equipments[0][CONF_NAME] == "Turbelle"
        assert equipments[0][CONF_TASKS] == ["pump_clean"]
        assert equipments[0][CONF_CUSTOM_TASKS] == ["Graisser"]

    async def test_a_second_equipment_gets_the_next_id(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        result = await hass.config_entries.options.async_init(loaded_entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": "add"}
        )
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {CONF_NAME: "Nanostream", CONF_PRESET: "tunze_nanostream"},
        )
        await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_TASKS: ["pump_clean"]}
        )
        await hass.async_block_till_done()
        assert [e[CONF_ID] for e in loaded_entry.options[CONF_EQUIPMENTS]] == [
            "tunze_1",
            "tunze_2",
        ]

    async def test_the_custom_preset_preselects_nothing(
        self, hass: HomeAssistant, entry_factory, setup
    ) -> None:
        entry = await setup(hass, entry_factory(brand="generic", equipments=[]))
        result = await hass.config_entries.options.async_init(entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": "add"}
        )
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_NAME: "Reactor", CONF_PRESET: "custom"}
        )
        assert schema_default(result, CONF_TASKS) == []


class TestOptionsFlowEdit:
    async def test_renaming_keeps_the_id(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        # The id is what the entities' unique_ids are built from: renaming
        # must not recreate them and lose their history.
        result = await hass.config_entries.options.async_init(loaded_entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": "edit"}
        )
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_ID: "tunze_1"}
        )
        assert result["step_id"] == "edit_equipment"

        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            {CONF_NAME: "Turbelle 6105", CONF_TASKS: ["pump_clean"]},
        )
        await hass.async_block_till_done()

        equipments = loaded_entry.options[CONF_EQUIPMENTS]
        assert equipments[0][CONF_ID] == "tunze_1"
        assert equipments[0][CONF_NAME] == "Turbelle 6105"
        assert equipments[0][CONF_TASKS] == ["pump_clean"]

    async def test_edit_form_is_prefilled_with_the_current_values(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        result = await hass.config_entries.options.async_init(loaded_entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": "edit"}
        )
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_ID: "tunze_1"}
        )
        assert schema_default(result, CONF_NAME) == "Turbelle 6095"
        assert schema_default(result, CONF_TASKS) == [
            "pump_clean",
            "wear_parts_replace",
        ]


class TestOptionsFlowRemove:
    async def test_removing_drops_the_equipment(
        self, hass: HomeAssistant, loaded_entry
    ) -> None:
        result = await hass.config_entries.options.async_init(loaded_entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": "remove"}
        )
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_ID: "tunze_1"}
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        await hass.async_block_till_done()
        assert loaded_entry.options[CONF_EQUIPMENTS] == []

    async def test_removing_one_of_two_keeps_the_other(
        self, hass: HomeAssistant, entry_factory, make_equipment, setup
    ) -> None:
        entry = await setup(
            hass,
            entry_factory(
                equipments=[
                    make_equipment(),
                    make_equipment(
                        "tunze_2", "Nano", "tunze_nanostream", ["pump_clean"]
                    ),
                ]
            ),
        )
        result = await hass.config_entries.options.async_init(entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {"next_step_id": "remove"}
        )
        await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_ID: "tunze_1"}
        )
        await hass.async_block_till_done()
        assert [e[CONF_ID] for e in entry.options[CONF_EQUIPMENTS]] == ["tunze_2"]
