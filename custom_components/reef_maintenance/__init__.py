"""The Reef maintenance integration.

Tracks cleaning and wear tasks for equipment Home Assistant cannot talk to —
flow pumps, return pumps, skimmers — and publishes them with the same
`reef_role` entity contract as ha-reefbeat-component and
ha-aquamedic-component, so they land in the same ha-reef-card maintenance view
and are picked up by the same alert blueprints.

One config entry per brand; each equipment is a device under it.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .catalog import (
    CATALOG_PLATFORMS,
    CATALOG_SPEC,
    CATALOG_UNIQUE_ID,
    async_catalog_view,
    async_request_catalog_entry,
    brands,
    is_catalog_entry,
)
from .catalog_runtime import (
    async_setup_catalog,
    async_unload_catalog,
    signal_catalog_changed,
)
from .const import (
    ATTR_LAST_RESET,
    CONF_BRAND,
    CONF_EQUIPMENTS,
    CONF_ID,
    DOMAIN,
    PLATFORMS,
    SERVICE_RESET,
)
from .entity import brand_device_id
from .storage import MaintenanceStore, build_equipments

# Home Assistant validates with probatio, voluptuous being only an alias of it
# at runtime (2026.9), and types its flow helpers with probatio schemas since
# 2026.10. Older versions only have voluptuous.
if TYPE_CHECKING:
    import probatio as vol
else:
    try:
        import probatio as vol
    except ImportError:  # pragma: no cover - depends on the installed HA version
        import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

SERVICE_RESET_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_ids,
        vol.Optional(ATTR_LAST_RESET): cv.datetime,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the catalog entry, or one brand entry and its equipments."""
    if is_catalog_entry(entry):
        # The dedicated catalog entry owns the shared updater and carries the
        # update/auto-update entities.
        await async_setup_catalog(hass, entry, CATALOG_SPEC)
        await hass.config_entries.async_forward_entry_setups(entry, CATALOG_PLATFORMS)
        return True

    # Brand entry: make sure the catalog entry exists, then read the view — the
    # live one if the catalog is already up, else the built-in snapshot.
    async_request_catalog_entry(hass)
    view = await async_catalog_view(hass)
    lang = hass.config.language

    store = MaintenanceStore(hass, entry.entry_id)
    await store.async_load()

    equipments = build_equipments(dict(entry.options), view, lang)

    # The brand device is the via_device parent of every equipment, so the
    # UI groups them instead of listing a flat pile of pumps.
    brand = entry.data[CONF_BRAND]
    brand_label = brands(view).get(brand, brand.capitalize())
    brand_dev = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, brand_device_id(brand))},
        name=brand_label,
        manufacturer=brand_label,
        model="Maintenance",
        entry_type=dr.DeviceEntryType.SERVICE,
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "store": store,
        "equipments": equipments,
        "brand_device_id": brand_dev.id,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    @callback
    def _reload_on_catalog_change() -> None:
        # A new catalog release can change the tasks of an equipment, so reload
        # to follow it. The shared updater fires this same signal on its own
        # teardown, and reacting to that would re-enter setup on a closing event
        # loop: skip it when HA is stopping, when this entry is already on its
        # way out, or when the catalog entry itself is unloading.
        if hass.is_stopping or entry.state is not ConfigEntryState.LOADED:
            return
        catalog = hass.config_entries.async_entry_for_domain_unique_id(
            DOMAIN, CATALOG_UNIQUE_ID
        )
        if catalog is None or catalog.state is ConfigEntryState.UNLOAD_IN_PROGRESS:
            return
        hass.config_entries.async_schedule_reload(entry.entry_id)

    entry.async_on_unload(
        async_dispatcher_connect(
            hass, signal_catalog_changed(DOMAIN), _reload_on_catalog_change
        )
    )
    _async_register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the catalog entry or a brand entry."""
    if is_catalog_entry(entry):
        unloaded = await hass.config_entries.async_unload_platforms(
            entry, CATALOG_PLATFORMS
        )
        if unloaded:
            await async_unload_catalog(hass, entry, CATALOG_SPEC)
        return unloaded

    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when the equipment list changed: the entity set changes with it."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant, entry: ConfigEntry, device: dr.DeviceEntry
) -> bool:
    """Allow deleting an equipment straight from its device page.

    The brand device itself is not removable: it is the entry, not a piece of
    gear. Removing an equipment drops its definition from the options (which
    reloads the entry) and forgets its stored history.
    """
    identifier = next(
        (value for domain, value in device.identifiers if domain == DOMAIN), None
    )
    if identifier is None or identifier == brand_device_id(entry.data[CONF_BRAND]):
        return False

    remaining = [
        item
        for item in entry.options.get(CONF_EQUIPMENTS, [])
        if item.get(CONF_ID) != identifier
    ]
    store: MaintenanceStore = hass.data[DOMAIN][entry.entry_id]["store"]
    await store.async_forget_equipment(identifier)
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, CONF_EQUIPMENTS: remaining}
    )
    return True


def _async_register_services(hass: HomeAssistant) -> None:
    """Register the reset service once, whatever the number of entries.

    Its point is automation: stick an NFC tag next to the pump, scan it after
    cleaning, and the task is acknowledged without opening the dashboard.
    """
    if hass.services.has_service(DOMAIN, SERVICE_RESET):
        return

    async def _async_reset(call: ServiceCall) -> None:
        registry = er.async_get(hass)
        when = call.data.get(ATTR_LAST_RESET)
        for entity_id in call.data["entity_id"]:
            target = _resolve_instance(hass, registry, entity_id)
            if target is None:
                _LOGGER.warning("%s is not a reef_maintenance task entity", entity_id)
                continue
            store, equipment_id, task_key = target
            await store.async_reset(equipment_id, task_key, when)

    hass.services.async_register(
        DOMAIN, SERVICE_RESET, _async_reset, schema=SERVICE_RESET_SCHEMA
    )


def _resolve_instance(
    hass: HomeAssistant, registry: er.EntityRegistry, entity_id: str
) -> tuple[MaintenanceStore, str, str] | None:
    """Map an entity_id back to its (store, equipment_id, task_key).

    Any of the four entities of a task is accepted, since they all share the
    same instance; only the unique_id suffix differs.
    """
    record = registry.async_get(entity_id)
    if record is None or record.platform != DOMAIN or record.config_entry_id is None:
        return None

    data: dict[str, Any] | None = hass.data.get(DOMAIN, {}).get(record.config_entry_id)
    if data is None:
        return None

    for equipment in data["equipments"]:
        for instance in equipment.tasks:
            prefix = f"{equipment.id}_{instance.task.key}_"
            if record.unique_id.startswith(prefix):
                return data["store"], equipment.id, instance.task.key
    return None
