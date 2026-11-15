"""ReefTech equipment catalog, the source of every equipment and its tasks.

The hardcoded presets are gone: brands, models (items), generic kinds
(categories) and the maintenance tasks all come from the `equipment` section of
reeftech-catalog, read through the shared client (``catalog_runtime`` +
``catalog_pack``). Offline and before the first download, the built-in snapshot
shipped with the integration (``catalog_builtin/``) is used instead.

A choice in the config flow is stored as ``item:<id>`` or ``category:<id>``;
``resolve_equipment_tasks`` turns it into the task list (category tasks,
overridden by the item's), localized to the Home Assistant language.
"""

from __future__ import annotations

from typing import Any, Final

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.util import slugify

from .catalog_pack import Layer, build_view, resolve_maintenance
from .catalog_runtime import BUILTIN_DIR, CatalogSpec, get_updater
from .const import DOMAIN
from .tasks import DAYS_PER_UNIT, MaintenanceTask

SECTION: Final = "equipment"
SCOPES: Final = ("aquarium",)

CATALOG_SPEC: Final = CatalogSpec(DOMAIN, SECTION, "ReefTech equipment catalog", SCOPES)

# The catalog lives in a dedicated config entry (like ha-reefbeat-component's
# supplements catalog): it owns the shared updater and carries the update and
# auto-update entities, so brand entries only read the view. Keeping the
# updater off the brand entries is also what lets the test harness tear the
# updater's timer and task down cleanly with its own entry.
CONF_CATALOG: Final = "equipment_catalog"
CATALOG_UNIQUE_ID: Final = "catalog_equipment"
SOURCE_CATALOG: Final = "catalog"
CATALOG_PLATFORMS: Final[list[Platform]] = [Platform.SWITCH, Platform.UPDATE]


def is_catalog_entry(entry: ConfigEntry) -> bool:
    """Whether a config entry of the integration is the equipment catalog."""
    return bool(entry.data.get(CONF_CATALOG))


@callback
def async_request_catalog_entry(hass: HomeAssistant) -> None:
    """Create the catalog entry if there is none yet (called by brand entries)."""
    entries = hass.config_entries
    if entries.async_entry_for_domain_unique_id(DOMAIN, CATALOG_UNIQUE_ID):
        return
    if entries.flow.async_progress_by_handler(
        DOMAIN, match_context={"source": SOURCE_CATALOG}
    ):
        return
    hass.async_create_task(
        entries.flow.async_init(DOMAIN, context={"source": SOURCE_CATALOG}),
        "reef_maintenance equipment catalog entry",
    )


# Brand of the generic categories ("a kind of gear, without the exact model").
GENERIC_BRAND: Final = "generic"
GENERIC_LABEL: Final = "Other / generic"

# Prefixes of a stored catalog reference.
ITEM: Final = "item:"
CATEGORY: Final = "category:"

# Equipment of entries created before the catalog migration referenced a preset
# id; map the retired presets onto their catalog equivalents so those entries
# keep their model and tasks after the upgrade.
LEGACY_PRESETS: Final[dict[str, str]] = {
    "tunze_turbelle_stream": f"{ITEM}tunze-turbelle-stream",
    "tunze_nanostream": f"{ITEM}tunze-nanostream",
    "tunze_silence": f"{ITEM}tunze-silence",
    "jebao_flow": f"{ITEM}jebao-flow",
    "jebao_return": f"{ITEM}jebao-return",
    "generic_flow_dc": f"{CATEGORY}circulation_pump",
    "generic_return_dc": f"{CATEGORY}return_pump",
    "generic_needle_skimmer": f"{CATEGORY}skimmer",
    "generic_heater": f"{CATEGORY}heater",
    "generic_routine": f"{CATEGORY}aquarium",
}


def _builtin_view() -> dict[str, Any]:
    """Build the view from the shipped snapshot (blocking file IO)."""
    layer = Layer("builtin", BUILTIN_DIR, "", "builtin")
    return build_view([layer], SECTION, SCOPES)


async def async_catalog_view(hass: HomeAssistant) -> dict[str, Any]:
    """Return the merged catalog view: the live one, else the built-in snapshot."""
    updater = get_updater(hass, DOMAIN)
    if updater is not None:
        return await updater.async_view()
    return await hass.async_add_executor_job(_builtin_view)


def localize(i18n: dict[str, str] | None, lang: str) -> str | None:
    """Pick a language from an i18n mapping, falling back to English then any."""
    if not i18n:
        return None
    return i18n.get(lang) or i18n.get("en") or next(iter(i18n.values()), None)


def brands(view: dict[str, Any]) -> dict[str, str]:
    """Brand id -> label: the generic kinds, plus every item brand."""
    out = {GENERIC_BRAND: GENERIC_LABEL}
    for item in view.get("items", {}).values():
        label = item.get("brand")
        if label:
            out[slugify(label)] = label
    return out


def choices(view: dict[str, Any], brand: str, lang: str) -> list[tuple[str, str]]:
    """(stored source, label) pairs offered for a brand, sorted by label.

    Generic brand -> the categories; a real brand -> its items.
    """
    pairs: list[tuple[str, str]] = []
    if brand == GENERIC_BRAND:
        for cid, cat in view.get("categories", {}).items():
            label = localize(cat.get("name"), lang) or cid
            pairs.append((f"{CATEGORY}{cid}", label))
    else:
        for iid, item in view.get("items", {}).items():
            if slugify(item.get("brand", "")) != brand:
                continue
            label = localize(item.get("name"), lang) or item.get("model") or iid
            pairs.append((f"{ITEM}{iid}", label))
    return sorted(pairs, key=lambda pair: pair[1].casefold())


def split_source(source: str) -> tuple[str | None, str | None]:
    """Return (item_id, category_id) from a stored ``item:``/``category:`` ref."""
    if source.startswith(ITEM):
        return source[len(ITEM) :], None
    if source.startswith(CATEGORY):
        return None, source[len(CATEGORY) :]
    return None, None


def model_label(view: dict[str, Any], source: str, lang: str) -> str:
    """Human label of a source, for the HA device model."""
    item_id, category_id = split_source(source)
    if item_id is not None:
        item = view.get("items", {}).get(item_id, {})
        return localize(item.get("name"), lang) or item.get("model") or item_id
    category = view.get("categories", {}).get(category_id, {})
    return localize(category.get("name"), lang) or (category_id or source)


def _task_from_catalog(entry: dict[str, Any]) -> MaintenanceTask:
    """Turn one resolved catalog task into a MaintenanceTask (days internally)."""
    schedule = entry.get("schedule") or {}
    unit = schedule.get("unit", "weeks")
    if unit not in DAYS_PER_UNIT:
        unit = "weeks"
    factor = DAYS_PER_UNIT[unit]
    every = schedule.get("every") or {}
    default = max(1, int(every.get("default", 4)))
    low = max(1, int(every.get("min", 1)))
    high = max(low, int(every.get("max", 52)))
    return MaintenanceTask(
        key=entry["task"],
        default_days=default * factor,
        min_days=low * factor,
        max_days=high * factor,
        icon=entry.get("icon") or "mdi:wrench-check",
        unit=unit,
    )


def resolve_equipment_tasks(
    view: dict[str, Any], source: str, lang: str
) -> dict[str, tuple[MaintenanceTask, str]]:
    """Task id -> (MaintenanceTask, localized name) an equipment would get."""
    item_id, category_id = split_source(source)
    out: dict[str, tuple[MaintenanceTask, str]] = {}
    for entry in resolve_maintenance(view, item_id, category_id):
        name = localize(entry.get("name"), lang) or entry["task"].replace("_", " ")
        out[entry["task"]] = (_task_from_catalog(entry), name)
    return out
