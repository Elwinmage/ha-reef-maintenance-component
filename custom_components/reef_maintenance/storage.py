"""Persistent maintenance state, and the runtime model of an equipment.

Two storages, on purpose:

- ``entry.options`` holds the *definition* of the equipments (id, name,
  preset, task list). It changes rarely and a change reloads the entry, which
  is exactly what we want since the entity set changes with it.
- this ``Store`` holds the *state*: last reset, interval overrides and
  notification flags. It changes on every button press, and must never
  trigger a reload.

A maintenance instance is identified by ``(equipment_id, task_key)``.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Final

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.storage import Store
from homeassistant.util import slugify

from .const import (
    CONF_CUSTOM_TASKS,
    CONF_EQUIPMENTS,
    CONF_ID,
    CONF_NAME,
    CONF_PRESET,
    CONF_TASKS,
)
from .presets import get_preset
from .tasks import MaintenanceTask, custom_task, get_task

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION: Final[int] = 1
STORAGE_KEY_TPL: Final[str] = "reef_maintenance_{entry_id}"


# =============================================================================
# Equipment model
# =============================================================================


@dataclass(frozen=True, slots=True)
class TaskInstance:
    """A task attached to an equipment, ready to be turned into entities."""

    task: MaintenanceTask
    # Free-text label of a user-defined task, injected through
    # translation_placeholders. None for library tasks, which HA translates.
    label: str | None = None


@dataclass(frozen=True, slots=True)
class Equipment:
    """One physical piece of gear, rendered as a device in Home Assistant."""

    id: str
    name: str
    preset_id: str
    tasks: tuple[TaskInstance, ...] = field(default_factory=tuple)
    part_number: str | None = None

    @property
    def model(self) -> str:
        """Return the model label shown on the HA device."""
        preset = get_preset(self.preset_id)
        return preset.model if preset else self.preset_id


def build_equipment(payload: dict[str, Any]) -> Equipment:
    """Turn one stored equipment definition into its runtime model.

    Unknown task keys are skipped rather than fatal: a downgrade, or a task
    dropped from the library, must not prevent the entry from loading.
    """
    preset = get_preset(payload.get(CONF_PRESET, ""))
    overrides = {spec.key: spec.resolve() for spec in (preset.tasks if preset else ())}

    instances: list[TaskInstance] = []
    for key in payload.get(CONF_TASKS, []):
        # A preset override wins over the library defaults.
        task = overrides.get(key) or get_task(key)
        if task is None:
            _LOGGER.warning("Unknown maintenance task %r, ignored", key)
            continue
        instances.append(TaskInstance(task))

    for label in payload.get(CONF_CUSTOM_TASKS, []):
        slug = slugify(label)
        if not slug:
            continue
        instances.append(TaskInstance(custom_task(slug), label=label))

    return Equipment(
        id=payload[CONF_ID],
        name=payload[CONF_NAME],
        preset_id=payload.get(CONF_PRESET, ""),
        tasks=tuple(instances),
        part_number=preset.part_number if preset else None,
    )


def build_equipments(options: dict[str, Any]) -> list[Equipment]:
    """Turn the whole options payload into runtime equipments."""
    return [build_equipment(item) for item in options.get(CONF_EQUIPMENTS, [])]


def next_equipment_id(options: dict[str, Any], brand: str) -> str:
    """Return a fresh, stable equipment id such as `tunze_3`.

    Ids are never derived from the name: renaming an equipment must not
    recreate its entities and lose their history.
    """
    used = {item.get(CONF_ID, "") for item in options.get(CONF_EQUIPMENTS, [])}
    index = 1
    while f"{brand}_{index}" in used:
        index += 1
    return f"{brand}_{index}"


# =============================================================================
# Persistent state
# =============================================================================


def _instance_id(equipment_id: str, task_key: str) -> str:
    return f"{equipment_id}:{task_key}"


@dataclass(slots=True)
class MaintenanceState:
    """In-memory state of a single maintenance instance."""

    last_reset: datetime | None = None
    interval_days: int | None = None  # None means "use the task default"
    notify: bool = True


class MaintenanceStore:
    """Persistent maintenance state for one config entry."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, STORAGE_KEY_TPL.format(entry_id=entry_id)
        )
        self._data: dict[str, MaintenanceState] = {}
        self._listeners: dict[str, list[Callable[[], None]]] = {}
        self._loaded = False

    # ---- loading / saving ------------------------------------------------

    async def async_load(self) -> None:
        """Load persisted state (no-op when already loaded)."""
        if self._loaded:
            return
        raw = await self._store.async_load() or {}
        for iid, payload in (raw.get("instances") or {}).items():
            self._data[iid] = MaintenanceState(
                last_reset=parse_dt(payload.get("last_reset")),
                interval_days=payload.get("interval_days"),
                notify=payload.get("notify", True) is not False,
            )
        self._loaded = True

    async def _async_save(self) -> None:
        out: dict[str, dict[str, Any]] = {}
        for iid, state in self._data.items():
            entry: dict[str, Any] = {}
            if state.last_reset is not None:
                entry["last_reset"] = state.last_reset.isoformat()
            if state.interval_days is not None:
                entry["interval_days"] = state.interval_days
            # Only the non-default value is persisted, to keep the file lean.
            if not state.notify:
                entry["notify"] = False
            if entry:
                out[iid] = entry
        await self._store.async_save({"instances": out})

    async def async_forget_equipment(self, equipment_id: str) -> None:
        """Drop every instance of an equipment that was removed."""
        prefix = f"{equipment_id}:"
        stale = [iid for iid in self._data if iid.startswith(prefix)]
        for iid in stale:
            del self._data[iid]
        if stale:
            await self._async_save()

    # ---- read ------------------------------------------------------------

    def get_state(self, equipment_id: str, task_key: str) -> MaintenanceState:
        """Return the state of an instance, creating it on first access."""
        iid = _instance_id(equipment_id, task_key)
        state = self._data.get(iid)
        if state is None:
            state = MaintenanceState()
            self._data[iid] = state
        return state

    def get_last_reset(self, equipment_id: str, task_key: str) -> datetime | None:
        return self.get_state(equipment_id, task_key).last_reset

    def get_interval(self, equipment_id: str, task_key: str, default: int) -> int:
        value = self.get_state(equipment_id, task_key).interval_days
        return value if value is not None else default

    def get_notify(self, equipment_id: str, task_key: str) -> bool:
        return self.get_state(equipment_id, task_key).notify

    # ---- write -----------------------------------------------------------

    async def async_reset(
        self, equipment_id: str, task_key: str, when: datetime | None = None
    ) -> datetime:
        """Record a maintenance event, defaulting to now."""
        stamp = when or datetime.now(timezone.utc)
        self.get_state(equipment_id, task_key).last_reset = stamp
        await self._async_save()
        self._notify(_instance_id(equipment_id, task_key))
        return stamp

    async def async_set_interval(
        self, equipment_id: str, task_key: str, days: int
    ) -> None:
        self.get_state(equipment_id, task_key).interval_days = int(days)
        await self._async_save()
        self._notify(_instance_id(equipment_id, task_key))

    async def async_set_notify(
        self, equipment_id: str, task_key: str, enabled: bool
    ) -> None:
        self.get_state(equipment_id, task_key).notify = bool(enabled)
        await self._async_save()
        self._notify(_instance_id(equipment_id, task_key))

    # ---- listeners -------------------------------------------------------

    @callback
    def async_add_listener(
        self, equipment_id: str, task_key: str, cb: Callable[[], None]
    ) -> Callable[[], None]:
        """Subscribe to changes of one instance; returns an unsubscribe."""
        iid = _instance_id(equipment_id, task_key)
        self._listeners.setdefault(iid, []).append(cb)

        def _unsub() -> None:
            listeners = self._listeners.get(iid)
            if listeners and cb in listeners:
                listeners.remove(cb)

        return _unsub

    def _notify(self, iid: str) -> None:
        for cb in list(self._listeners.get(iid, [])):
            try:
                cb()
            except Exception:  # pragma: no cover - defensive
                _LOGGER.exception("MaintenanceStore listener raised")


# =============================================================================
# Derived calculations
# =============================================================================


def compute_days_left(
    last_reset: datetime | None, interval_days: int, now: datetime | None = None
) -> int | None:
    """Days left before the task is due; negative when overdue.

    ``None`` means "never reset": the task is pending a first acknowledgement
    rather than overdue, which matters right after adding an equipment.
    """
    if last_reset is None:
        return None
    ref = now or datetime.now(timezone.utc)
    remaining = interval_days - (ref - last_reset).total_seconds() / 86400.0
    # Floor away from zero: a partially used day counts, in both directions.
    return int(remaining) if remaining >= 0 else -int(-remaining + 0.999999)


def is_overdue(
    last_reset: datetime | None, interval_days: int, now: datetime | None = None
) -> bool:
    """Return True when the task is past its interval."""
    days_left = compute_days_left(last_reset, interval_days, now)
    return days_left is not None and days_left < 0


def parse_dt(value: Any) -> datetime | None:
    """Parse an ISO-8601 string into an aware datetime, or return None."""
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
