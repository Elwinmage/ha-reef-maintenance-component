"""Constants for the Reef maintenance integration."""

from __future__ import annotations

from typing import Final

from homeassistant.const import Platform

DOMAIN: Final[str] = "reef_maintenance"

# Platforms of a brand entry (its equipments' task entities). The catalog's own
# update/auto-update entities live on the dedicated catalog entry instead
# (see catalog.CATALOG_PLATFORMS).
PLATFORMS: Final[list[Platform]] = [
    Platform.BUTTON,
    Platform.DATE,
    Platform.NUMBER,
    Platform.SWITCH,
]

# ── Config entry keys ─────────────────────────────────────────────────────
# entry.data holds what never changes: the brand this entry represents.
CONF_BRAND: Final[str] = "brand"

# entry.options holds the equipment definitions. State (last reset, interval
# overrides, notification flags) lives in the Store instead, because updating
# options reloads the entry — fine when the entity set changes, unacceptable
# on every button press.
CONF_EQUIPMENTS: Final[str] = "equipments"
CONF_ID: Final[str] = "id"
CONF_NAME: Final[str] = "name"
# Catalog reference of an equipment, as "item:<id>" or "category:<id>".
CONF_SOURCE: Final[str] = "source"
# Display model, resolved from the catalog when the equipment is added and
# stored so the device keeps its label even if the catalog changes.
CONF_MODEL: Final[str] = "model"
CONF_TASKS: Final[str] = "tasks"
CONF_CUSTOM_TASKS: Final[str] = "custom_tasks"

# Legacy key (pre-catalog): equipment used to reference a hardcoded preset.
# Still read so entries created before the migration keep loading.
CONF_PRESET: Final[str] = "preset"

# ── Services ──────────────────────────────────────────────────────────────
SERVICE_RESET: Final[str] = "reset"
ATTR_LAST_RESET: Final[str] = "last_reset"
