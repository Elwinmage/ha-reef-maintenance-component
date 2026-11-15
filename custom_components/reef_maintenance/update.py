"""The equipment-catalog update entity.

Only the entry that owns the shared updater carries it: it shows the installed
and latest catalog release and installs a new one on demand. The entity itself
lives in the shared client (``catalog_runtime``).
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .catalog_runtime import catalog_entities
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add the catalog update entity for the owner entry (none for the others)."""
    async_add_entities(catalog_entities(hass, entry, DOMAIN, "update"))
