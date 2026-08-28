"""Test fixtures for the Reef maintenance integration.

Built for `pytest-homeassistant-custom-component`. This integration talks to
no hardware and to no network, so there is nothing to mock away: the fixtures
here only build config entries and load the integration.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

# Make `custom_components` importable when pytest is run from the repo root.
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from custom_components.reef_maintenance.const import ( # noqa: E402
    CONF_BRAND,
    CONF_CUSTOM_TASKS,
    CONF_EQUIPMENTS,
    CONF_ID,
    CONF_NAME,
    CONF_PRESET,
    CONF_TASKS,
    DOMAIN,
)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Load `custom_components` in every test.

    Without it Home Assistant refuses to set up an integration that is not
    part of core, and every setup test fails with "Integration not found".
    """
    yield


def equipment(
    equipment_id: str = "tunze_1",
    name: str = "Turbelle 6095",
    preset: str = "tunze_turbelle_stream",
    tasks: list[str] | None = None,
    custom_tasks: list[str] | None = None,
) -> dict[str, Any]:
    """Build one equipment definition, as stored in `entry.options`."""
    return {
        CONF_ID: equipment_id,
        CONF_NAME: name,
        CONF_PRESET: preset,
        CONF_TASKS: ["pump_clean", "wear_parts_replace"] if tasks is None else tasks,
        CONF_CUSTOM_TASKS: custom_tasks or [],
    }


def make_entry(
    brand: str = "tunze",
    equipments: list[dict[str, Any]] | None = None,
    entry_id: str = "test_entry",
) -> MockConfigEntry:
    """Build a config entry holding a brand and its equipments."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=brand.capitalize(),
        data={CONF_BRAND: brand},
        options={
            CONF_EQUIPMENTS: equipments if equipments is not None else [equipment()]
        },
        unique_id=brand,
        entry_id=entry_id,
    )


@pytest.fixture
def entry() -> MockConfigEntry:
    """A Tunze entry with a single Turbelle and two tasks."""
    return make_entry()


async def setup_entry(hass: HomeAssistant, entry: MockConfigEntry) -> MockConfigEntry:
    """Add an entry to hass and set it up, returning it once loaded."""
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


@pytest.fixture
async def loaded_entry(hass: HomeAssistant, entry: MockConfigEntry) -> MockConfigEntry:
    """An entry already set up, with its four entities per task created."""
    return await setup_entry(hass, entry)


# The builders above are plain functions so they can be called with arguments
# mid-test; these fixtures are how other modules reach them, since `tests` is
# not a package and `from .conftest import ...` would fail.
@pytest.fixture
def make_equipment():
    """Return the `equipment()` builder."""
    return equipment


@pytest.fixture
def entry_factory():
    """Return the `make_entry()` builder."""
    return make_entry


@pytest.fixture
def setup():
    """Return the `setup_entry()` helper."""
    return setup_entry
