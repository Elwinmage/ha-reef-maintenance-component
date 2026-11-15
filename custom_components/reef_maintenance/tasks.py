"""Maintenance task model.

Tasks come from the ReefTech equipment catalog (see catalog.py). Each one is
turned into a `MaintenanceTask` (key = catalog task id, stored in days). Its
displayed name is the catalog's localized name, carried through
`translation_placeholders` on the generic `maint_custom` keys — the same path
user-defined tasks use — so only the fixed part ("(weeks)", "(last done)")
comes from translations/*.json. The task key still lands in the entity
unique_id and in `reef_role`, so acknowledgements survive a catalog update.
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


# Bounds of a user-defined task: 1 to 104 weeks, defaulting to 4.
CUSTOM_TASK: Final[MaintenanceTask] = MaintenanceTask(
    key=CUSTOM_KEY,
    default_days=28,
    min_days=7,
    max_days=728,
    icon="mdi:wrench-check",
    unit="weeks",
)


def custom_task(slug: str) -> MaintenanceTask:
    """Build the task descriptor of a user-defined entry.

    The slug only identifies the instance (unique_id, storage key); the
    displayed label is carried by the entity's translation_placeholders.
    """
    return replace(CUSTOM_TASK, key=f"{CUSTOM_KEY}_{slug}")
