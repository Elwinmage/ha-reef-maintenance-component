"""Library of maintenance tasks.

This module holds every task the integration knows how to name. Presets
(see presets.py) never define their own wording: they reference a library key
and may override the interval bounds. That split is what keeps translation
work bounded — adding a brand costs zero new strings as long as it reuses
existing tasks.

Entity naming goes through Home Assistant's normal translation machinery
(`translation_key` + translations/*.json), so a task is retranslated when the
user changes the HA language. User-defined tasks cannot work that way: they
reuse the generic `maint_custom` keys and inject the free-text label through
`translation_placeholders`, so only the fixed part ("(weeks)", "(last done)")
stays translated.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Final

# Role prefix shared with ha-reefbeat-component and ha-aquamedic-component.
# ha-reef-card's maintenance view scans for entities whose `reef_role` starts
# with it, so it must not change.
ROLE_PREFIX: Final[str] = "maint_"

# Task key used by every user-defined task. The label lives in the entity's
# translation_placeholders, not in a dedicated translation key.
CUSTOM_KEY: Final[str] = "custom"

VALID_UNITS: Final[tuple[str, ...]] = ("days", "weeks", "months")

# Days per display unit. Storage is always in days so `days_left` stays
# comparable across tasks, integrations and cards.
DAYS_PER_UNIT: Final[dict[str, int]] = {"days": 1, "weeks": 7, "months": 30}


@dataclass(frozen=True, slots=True)
class MaintenanceTask:
    """A single maintenance task.

    `key` is stable forever: it lands in the entity unique_id and in the
    storage key, so renaming one loses the user's reset history.
    """

    key: str
    default_days: int
    min_days: int
    max_days: int
    icon: str = "mdi:wrench-check"
    unit: str = "weeks"

    @property
    def translation_key(self) -> str:
        """Return the translation key, also exposed as `reef_role`."""
        return f"{ROLE_PREFIX}{self.key}"


def _task(
    key: str,
    default_days: int,
    min_days: int,
    max_days: int,
    icon: str,
    unit: str,
) -> MaintenanceTask:
    return MaintenanceTask(key, default_days, min_days, max_days, icon, unit)


# The library. Defaults are starting points: every one of them is adjustable
# per equipment through the interval number entity.
LIBRARY: Final[dict[str, MaintenanceTask]] = {
    t.key: t
    for t in (
        # ── Pumps ────────────────────────────────────────────────────────
        _task("pump_clean", 45, 30, 90, "mdi:fan", "weeks"),
        _task("magnet_holder_clean", 45, 30, 120, "mdi:magnet", "weeks"),
        _task("strainer_clean", 42, 21, 63, "mdi:filter-variant", "weeks"),
        _task("pump_descale", 180, 90, 365, "mdi:spray-bottle", "months"),
        _task("wear_parts_replace", 730, 365, 1095, "mdi:cog-refresh", "months"),
        # ── Skimmers ─────────────────────────────────────────────────────
        _task("skimmer_cup_clean", 14, 7, 28, "mdi:cup-water", "weeks"),
        _task("venturi_clean", 28, 14, 56, "mdi:weather-windy", "weeks"),
        _task("needle_wheel_clean", 60, 30, 120, "mdi:fan", "months"),
        _task("skimmer_body_descale", 180, 90, 365, "mdi:spray-bottle", "months"),
        # ── Filtration and media ─────────────────────────────────────────
        _task("sock_replace", 7, 3, 21, "mdi:sack", "days"),
        _task("carbon_replace", 30, 14, 60, "mdi:grain", "weeks"),
        _task("resin_replace", 60, 30, 120, "mdi:dots-hexagon", "months"),
        # ── Probes and lighting ──────────────────────────────────────────
        _task("probe_calibrate", 90, 30, 180, "mdi:tune-variant", "months"),
        _task("probe_clean", 60, 30, 120, "mdi:test-tube", "months"),
        _task("uv_lamp_replace", 365, 180, 540, "mdi:lightbulb-alert", "months"),
        # ── Routine ──────────────────────────────────────────────────────
        _task("water_change", 14, 7, 364, "mdi:water-sync", "weeks"),
        _task("glass_clean", 7, 3, 21, "mdi:square-opacity", "days"),
        _task("icp_test", 90, 30, 180, "mdi:flask-outline", "months"),
        _task("rodi_filter_replace", 180, 90, 365, "mdi:water-opacity", "months"),
        _task("sump_clean", 90, 30, 180, "mdi:waves-arrow-right", "months"),
        _task("sand_vacuum", 28, 14, 56, "mdi:vacuum", "weeks"),
    )
}

# Bounds of a user-defined task: 1 to 104 weeks, defaulting to 4.
CUSTOM_TASK: Final[MaintenanceTask] = MaintenanceTask(
    key=CUSTOM_KEY,
    default_days=28,
    min_days=7,
    max_days=728,
    icon="mdi:wrench-check",
    unit="weeks",
)


def get_task(key: str) -> MaintenanceTask | None:
    """Return a library task, or None when the key is unknown."""
    return LIBRARY.get(key)


def custom_task(slug: str) -> MaintenanceTask:
    """Build the task descriptor of a user-defined entry.

    The slug only identifies the instance (unique_id, storage key); the
    displayed label is carried by the entity's translation_placeholders.
    """
    return replace(CUSTOM_TASK, key=f"{CUSTOM_KEY}_{slug}")


def is_custom(task: MaintenanceTask) -> bool:
    """Return True when the task is user-defined rather than from the library."""
    return task.key == CUSTOM_KEY or task.key.startswith(f"{CUSTOM_KEY}_")


def translation_key_for(task: MaintenanceTask) -> str:
    """Return the translation key to use for a task.

    Custom tasks all share the generic `maint_custom` keys; library tasks use
    their own.
    """
    return CUSTOM_TASK.translation_key if is_custom(task) else task.translation_key
