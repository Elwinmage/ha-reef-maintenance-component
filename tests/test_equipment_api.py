"""Adding, listing and removing equipment from the card (equipment_api.py)."""

from __future__ import annotations

from typing import Any

import pytest
from homeassistant.core import HomeAssistant

from custom_components.reef_maintenance import equipment_api as api
from custom_components.reef_maintenance.catalog import async_catalog_view
from custom_components.reef_maintenance.const import (
    CONF_BRAND,
    CONF_CUSTOM_TASKS,
    CONF_EQUIPMENTS,
    CONF_ID,
    CONF_NAME,
    CONF_SOURCE,
    CONF_TASKS,
    DOMAIN,
)

TURBELLE = "item:tunze-turbelle-stream"


async def test_brand_of_source(hass: HomeAssistant) -> None:
    view = await async_catalog_view(hass)
    assert api.brand_of_source(view, TURBELLE) == "tunze"
    assert api.brand_of_source(view, "category:heater") == "generic"
    for bad in ("item:nope", "category:nope", "nonsense"):
        with pytest.raises(ValueError, match="unknown equipment"):
            api.brand_of_source(view, bad)
    # An item without a brand goes with the generic ones
    view["items"]["no-brand"] = {"category": "heater"}
    assert api.brand_of_source(view, "item:no-brand") == "generic"


async def test_add_creates_the_brand_entry(hass: HomeAssistant) -> None:
    result = await api.async_add_equipment(hass, TURBELLE)
    await hass.async_block_till_done()
    assert result["equipment_id"] == "tunze_1"
    assert result["source"] == TURBELLE
    assert result["tasks"][:1] == ["pump_clean"]
    entry = hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, "tunze")
    assert entry is not None and entry.data == {CONF_BRAND: "tunze"}
    (item,) = entry.options[CONF_EQUIPMENTS]
    assert item[CONF_ID] == "tunze_1" and item[CONF_SOURCE] == TURBELLE
    assert item[CONF_NAME] == result["name"]
    assert item[CONF_TASKS] == result["tasks"] and item[CONF_CUSTOM_TASKS] == []


async def test_add_to_an_existing_entry(hass: HomeAssistant, loaded_entry: Any) -> None:
    result = await api.async_add_equipment(hass, TURBELLE, "Left pump")
    await hass.async_block_till_done()
    assert (result["equipment_id"], result["name"]) == ("tunze_2", "Left pump")
    ids = [item[CONF_ID] for item in loaded_entry.options[CONF_EQUIPMENTS]]
    assert ids == ["tunze_1", "tunze_2"]


async def test_generic_category(hass: HomeAssistant) -> None:
    result = await api.async_add_equipment(hass, "category:heater")
    await hass.async_block_till_done()
    assert result["equipment_id"] == "generic_1" and result["tasks"]


async def test_add_refuses_an_unknown_source(hass: HomeAssistant) -> None:
    with pytest.raises(ValueError, match="unknown equipment"):
        await api.async_add_equipment(hass, "item:nope")


async def test_creating_the_entry_may_fail(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def aborted(*args: Any, **kwargs: Any) -> dict[str, Any]:
        return {"type": "abort", "reason": "boom"}

    monkeypatch.setattr(hass.config_entries.flow, "async_init", aborted)
    with pytest.raises(ValueError, match="boom"):
        await api.async_add_equipment(hass, TURBELLE)


async def test_list(hass: HomeAssistant, loaded_entry: Any) -> None:
    (found,) = api.list_equipments(hass)
    assert found["equipment_id"] == "tunze_1"
    assert found["brand"] == "tunze" and found["entry_id"] == loaded_entry.entry_id
    assert found["tasks"] == ["pump_clean", "wear_parts_replace"]


async def test_remove(hass: HomeAssistant, loaded_entry: Any) -> None:
    assert await api.async_remove_equipment(hass, "tunze_1")
    await hass.async_block_till_done()
    assert loaded_entry.options[CONF_EQUIPMENTS] == []
    assert api.list_equipments(hass) == []
    assert not await api.async_remove_equipment(hass, "tunze_1")


async def test_remove_from_an_entry_not_loaded(
    hass: HomeAssistant, entry_factory: Any
) -> None:
    entry = entry_factory()
    entry.add_to_hass(hass)
    assert await api.async_remove_equipment(hass, "tunze_1")
    assert entry.options[CONF_EQUIPMENTS] == []


async def test_websocket_commands(
    hass: HomeAssistant, hass_ws_client: Any, loaded_entry: Any
) -> None:
    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/equipment/list"})
    reply = await client.receive_json()
    assert reply["success"]
    assert [e["equipment_id"] for e in reply["result"]["equipments"]] == ["tunze_1"]

    await client.send_json(
        {"id": 2, "type": f"{DOMAIN}/equipment/add", "source": TURBELLE, "name": "B"}
    )
    reply = await client.receive_json()
    assert reply["success"] and reply["result"]["equipment_id"] == "tunze_2"

    await client.send_json(
        {"id": 3, "type": f"{DOMAIN}/equipment/add", "source": "item:nope"}
    )
    reply = await client.receive_json()
    assert not reply["success"] and reply["error"]["code"] == "invalid_source"

    await client.send_json(
        {"id": 4, "type": f"{DOMAIN}/equipment/remove", "equipment_id": "tunze_2"}
    )
    reply = await client.receive_json()
    assert reply["success"] and reply["result"] == {"removed": True}

    await client.send_json(
        {"id": 5, "type": f"{DOMAIN}/equipment/remove", "equipment_id": "tunze_2"}
    )
    reply = await client.receive_json()
    assert not reply["success"] and reply["error"]["code"] == "not_found"


async def test_websocket_registration_is_idempotent(hass: HomeAssistant) -> None:
    api.async_setup_equipment_api(hass)
    api.async_setup_equipment_api(hass)


async def test_catalog_entry_is_requested_once(
    hass: HomeAssistant, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No second catalog entry is requested while its flow is already running."""
    from unittest.mock import AsyncMock, MagicMock

    from custom_components.reef_maintenance.catalog import async_request_catalog_entry

    init = AsyncMock()
    monkeypatch.setattr(hass.config_entries.flow, "async_init", init)
    monkeypatch.setattr(
        hass.config_entries.flow,
        "async_progress_by_handler",
        MagicMock(return_value=[{"flow_id": "running"}]),
    )
    async_request_catalog_entry(hass)
    await hass.async_block_till_done()
    init.assert_not_called()
