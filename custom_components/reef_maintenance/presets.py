"""Equipment presets, grouped by brand.

A preset is only a composition: a list of library task keys, optionally with
interval overrides, plus display metadata. Adding a brand therefore means
adding an entry here — and translation strings only if it needs a task the
library does not already have.

Interval values come from the manufacturer when one publishes a figure
(Tunze Turbelle: clean pump and magnet holder every 1-2 months; Tunze
Silence: full clean of pump and drive unit at least once a year; Jebao DCP:
monthly impeller cleaning; Jebao SLW: monthly to bi-monthly), and from reef
keeping practice otherwise. Both are starting points the user can change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from .tasks import LIBRARY, MaintenanceTask

# Brand of the "no specific brand" presets, and of user-defined equipment.
GENERIC_BRAND: Final[str] = "generic"

# Preset id of a fully user-defined equipment: no task is preselected, the
# user picks from the library and/or types free-text tasks.
CUSTOM_PRESET: Final[str] = "custom"


@dataclass(frozen=True, slots=True)
class TaskSpec:
    """Reference to a library task, with optional interval overrides."""

    key: str
    default_days: int | None = None
    min_days: int | None = None
    max_days: int | None = None

    def resolve(self) -> MaintenanceTask:
        """Return the library task with this preset's overrides applied."""
        base = LIBRARY[self.key]
        return MaintenanceTask(
            key=base.key,
            default_days=self.default_days or base.default_days,
            min_days=self.min_days or base.min_days,
            max_days=self.max_days or base.max_days,
            icon=base.icon,
            unit=base.unit,
        )


@dataclass(frozen=True, slots=True)
class Preset:
    """One equipment family: what it is called, and what it needs."""

    id: str
    brand: str
    # Shown in the config flow and stored as the HA device model.
    model: str
    tasks: tuple[TaskSpec, ...] = field(default_factory=tuple)
    # Spare part reference for wear_parts_replace, surfaced as a button
    # attribute so it is at hand when ordering.
    part_number: str | None = None


PRESETS: Final[dict[str, Preset]] = {
    p.id: p
    for p in (
        # ── Tunze ────────────────────────────────────────────────────────
        Preset(
            id="tunze_turbelle_stream",
            brand="tunze",
            model="Turbelle stream / stream 3",
            tasks=(
                TaskSpec("pump_clean", 45, 30, 90),
                TaskSpec("magnet_holder_clean", 45, 30, 90),
                TaskSpec("pump_descale", 180, 90, 365),
                TaskSpec("wear_parts_replace", 730, 365, 1095),
            ),
        ),
        Preset(
            id="tunze_nanostream",
            brand="tunze",
            model="Turbelle nanostream",
            tasks=(
                TaskSpec("pump_clean", 45, 30, 90),
                TaskSpec("magnet_holder_clean", 45, 30, 90),
                TaskSpec("pump_descale", 180, 90, 365),
                TaskSpec("wear_parts_replace", 730, 365, 1095),
            ),
        ),
        Preset(
            id="tunze_silence",
            brand="tunze",
            model="Silence / Silence PRO",
            tasks=(
                TaskSpec("strainer_clean", 42, 21, 63),
                TaskSpec("pump_clean", 90, 60, 180),
                # Manufacturer floor: complete disassembly at least yearly.
                TaskSpec("pump_descale", 365, 180, 540),
                TaskSpec("wear_parts_replace", 730, 365, 1095),
            ),
            part_number="1073.027 / 1073.047",
        ),
        # ── Jebao ────────────────────────────────────────────────────────
        Preset(
            id="jebao_flow",
            brand="jebao",
            model="SLW / MLW / SCP / SOW",
            tasks=(
                TaskSpec("pump_clean", 45, 30, 60),
                TaskSpec("magnet_holder_clean", 60, 30, 120),
                TaskSpec("pump_descale", 180, 90, 365),
                TaskSpec("wear_parts_replace", 540, 365, 1095),
            ),
        ),
        Preset(
            id="jebao_return",
            brand="jebao",
            model="DCP / MDP",
            tasks=(
                TaskSpec("strainer_clean", 30, 14, 60),
                TaskSpec("pump_clean", 30, 14, 60),
                TaskSpec("pump_descale", 180, 90, 365),
                TaskSpec("wear_parts_replace", 540, 365, 1095),
            ),
        ),
        # ── Generic, brand-independent ───────────────────────────────────
        Preset(
            id="generic_flow_dc",
            brand=GENERIC_BRAND,
            model="DC flow pump",
            tasks=(
                TaskSpec("pump_clean", 45, 30, 90),
                TaskSpec("magnet_holder_clean", 60, 30, 120),
                TaskSpec("pump_descale", 180, 90, 365),
                TaskSpec("wear_parts_replace", 540, 365, 1095),
            ),
        ),
        Preset(
            id="generic_return_dc",
            brand=GENERIC_BRAND,
            model="DC return pump",
            tasks=(
                TaskSpec("strainer_clean", 42, 21, 63),
                TaskSpec("pump_clean", 60, 30, 120),
                TaskSpec("pump_descale", 180, 90, 365),
                TaskSpec("wear_parts_replace", 540, 365, 1095),
            ),
        ),
        Preset(
            id="generic_needle_skimmer",
            brand=GENERIC_BRAND,
            model="Needle wheel skimmer",
            tasks=(
                TaskSpec("skimmer_cup_clean", 14, 7, 28),
                TaskSpec("venturi_clean", 28, 14, 56),
                TaskSpec("needle_wheel_clean", 60, 30, 120),
                TaskSpec("skimmer_body_descale", 180, 90, 365),
                TaskSpec("wear_parts_replace", 540, 365, 1095),
            ),
        ),
        Preset(
            id="generic_routine",
            brand=GENERIC_BRAND,
            model="Routine aquarium maintenance",
            tasks=(
                TaskSpec("water_change", 14, 7, 364),
                TaskSpec("glass_clean"),
                TaskSpec("icp_test"),
                TaskSpec("rodi_filter_replace"),
                TaskSpec("sump_clean"),
                TaskSpec("sand_vacuum"),
            ),
        ),
        # Fully user-defined: no preselected task.
        Preset(id=CUSTOM_PRESET, brand=GENERIC_BRAND, model="Custom equipment"),
    )
}

# Brand id -> display name. Brands are the unit of config entry: one entry
# per brand, equipments as sub-devices under it.
BRANDS: Final[dict[str, str]] = {
    "tunze": "Tunze",
    "jebao": "Jebao",
    GENERIC_BRAND: "Other / generic",
}


def presets_for_brand(brand: str) -> list[Preset]:
    """Return the presets of one brand, in declaration order."""
    return [p for p in PRESETS.values() if p.brand == brand]


def get_preset(preset_id: str) -> Preset | None:
    """Return a preset by id, or None when unknown (e.g. after a downgrade)."""
    return PRESETS.get(preset_id)
