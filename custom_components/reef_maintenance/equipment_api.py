"""Add, list and remove equipment from outside the config flow.

The card links a socket of a power strip to a piece of equipment of the catalog
(its `linked_equipment`); this module lets it go one step further, "keep the
maintenance of that equipment": it creates the equipment in this integration,
with the tasks the catalog gives it, and the card then records its id
(`linked_maintenance`). The tasks show up like any other, in the maintenance
view, with the same alerts.

The same operations as the options flow, behind three websocket commands (adding
and removing need an administrator):

- ``reef_maintenance/equipment/list``;
- ``reef_maintenance/equipment/add``: ``source`` (``item:<id>`` or
  ``category:<id>``, the catalog item the card gives as ``linked_equipment``)
  and an optional ``name``;
- ``reef_maintenance/equipment/remove``: ``equipment_id``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final

from homeassistant.components.websocket_api import async_register_command
from homeassistant.components.websocket_api.connection import ActiveConnection
from homeassistant.components.websocket_api.decorators import (
    async_response,
    require_admin,
    websocket_command,
)
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import slugify

from .catalog import (
    GENERIC_BRAND,
    async_catalog_view,
    is_catalog_entry,
    model_label,
    resolve_equipment_tasks,
    split_source,
)
from .const import (
    CONF_BRAND,
    CONF_CUSTOM_TASKS,
    CONF_EQUIPMENTS,
    CONF_ID,
    CONF_MODEL,
    CONF_NAME,
    CONF_SOURCE,
    CONF_TASKS,
    DOMAIN,
)
from .storage import MaintenanceStore, next_equipment_id

if TYPE_CHECKING:
    import probatio as vol
else:
    try:
        import probatio as vol
    except ImportError:  # pragma: no cover - depends on the installed HA version
        import voluptuous as vol

_REGISTERED: Final = "equipment_api_registered"


def brand_of_source(view: dict[str, Any], source: str) -> str:
    """Brand entry an equipment belongs to: its item's brand, or the generic one.

    @raise ValueError: a source the catalog does not know
    """
    item_id, category_id = split_source(source)
    if item_id is not None:
        item = view.get("items", {}).get(item_id)
        if item is None:
            raise ValueError(f"unknown equipment {source!r}")
        brand = slugify(item.get("brand", ""))
        return brand or GENERIC_BRAND
    if category_id is not None and category_id in view.get("categories", {}):
        return GENERIC_BRAND
    raise ValueError(f"unknown equipment {source!r}")


def _brand_entries(hass: HomeAssistant) -> list[ConfigEntry]:
    return [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if not is_catalog_entry(entry)
    ]


def list_equipments(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Every equipment of every brand entry, with its tasks."""
    found: list[dict[str, Any]] = []
    for entry in _brand_entries(hass):
        for item in entry.options.get(CONF_EQUIPMENTS, []):
            found.append(
                {
                    "equipment_id": item.get(CONF_ID),
                    "name": item.get(CONF_NAME),
                    "source": item.get(CONF_SOURCE),
                    "model": item.get(CONF_MODEL),
                    "brand": entry.data[CONF_BRAND],
                    "entry_id": entry.entry_id,
                    "tasks": list(item.get(CONF_TASKS, [])),
                }
            )
    return found


async def async_add_equipment(
    hass: HomeAssistant, source: str, name: str | None = None
) -> dict[str, Any]:
    """Create an equipment of the catalog, with the tasks the catalog gives it.

    The brand entry is created when it does not exist yet.

    @raise ValueError: a source the catalog does not know
    """
    view = await async_catalog_view(hass)
    lang = hass.config.language
    brand = brand_of_source(view, source)
    model = model_label(view, source, lang)
    tasks = list(resolve_equipment_tasks(view, source, lang))
    entry = hass.config_entries.async_entry_for_domain_unique_id(DOMAIN, brand)

    def make(options: dict[str, Any]) -> dict[str, Any]:
        return {
            CONF_ID: next_equipment_id(options, brand),
            CONF_NAME: name or model,
            CONF_SOURCE: source,
            CONF_MODEL: model,
            CONF_TASKS: tasks,
            CONF_CUSTOM_TASKS: [],
        }

    if entry is None:
        equipment = make({})
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": SOURCE_IMPORT},
            data={CONF_BRAND: brand, CONF_EQUIPMENTS: [equipment]},
        )
        if result.get("type") != "create_entry":
            raise ValueError(f"cannot create the {brand} entry: {result.get('reason')}")
    else:
        equipment = make(dict(entry.options))
        # The update listener of the entry reloads it with the new equipment
        hass.config_entries.async_update_entry(
            entry,
            options={
                **entry.options,
                CONF_EQUIPMENTS: [*entry.options.get(CONF_EQUIPMENTS, []), equipment],
            },
        )
    return {
        "equipment_id": equipment[CONF_ID],
        "name": equipment[CONF_NAME],
        "source": source,
        "tasks": tasks,
    }


async def async_remove_equipment(hass: HomeAssistant, equipment_id: str) -> bool:
    """Remove an equipment, its tasks and their history.

    @return: False when there is no such equipment
    """
    for entry in _brand_entries(hass):
        equipments = entry.options.get(CONF_EQUIPMENTS, [])
        if not any(item.get(CONF_ID) == equipment_id for item in equipments):
            continue
        data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
        if data is not None:
            store: MaintenanceStore = data["store"]
            await store.async_forget_equipment(equipment_id)
        hass.config_entries.async_update_entry(
            entry,
            options={
                **entry.options,
                CONF_EQUIPMENTS: [
                    item for item in equipments if item.get(CONF_ID) != equipment_id
                ],
            },
        )
        return True
    return False


def async_setup_equipment_api(hass: HomeAssistant) -> None:
    """Register the websocket commands (once per run)."""
    store = hass.data.setdefault(DOMAIN, {})
    if store.get(_REGISTERED):
        return
    store[_REGISTERED] = True

    @websocket_command({vol.Required("type"): f"{DOMAIN}/equipment/list"})
    @async_response
    async def ws_list(
        hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """The equipments kept, with their tasks."""
        connection.send_result(msg["id"], {"equipments": list_equipments(hass)})

    @websocket_command(
        {
            vol.Required("type"): f"{DOMAIN}/equipment/add",
            vol.Required("source"): str,
            vol.Optional("name"): str,
        }
    )
    @require_admin
    @async_response
    async def ws_add(
        hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Keep the maintenance of an equipment of the catalog."""
        try:
            result = await async_add_equipment(hass, msg["source"], msg.get("name"))
        except ValueError as err:
            connection.send_error(msg["id"], "invalid_source", str(err))
            return
        connection.send_result(msg["id"], result)

    @websocket_command(
        {
            vol.Required("type"): f"{DOMAIN}/equipment/remove",
            vol.Required("equipment_id"): str,
        }
    )
    @require_admin
    @async_response
    async def ws_remove(
        hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
    ) -> None:
        """Stop keeping the maintenance of an equipment."""
        if not await async_remove_equipment(hass, msg["equipment_id"]):
            connection.send_error(msg["id"], "not_found", "no such equipment")
            return
        connection.send_result(msg["id"], {"removed": True})

    for command in (ws_list, ws_add, ws_remove):
        async_register_command(hass, command)


__all__ = [
    "async_add_equipment",
    "async_remove_equipment",
    "async_setup_equipment_api",
    "brand_of_source",
    "list_equipments",
]
