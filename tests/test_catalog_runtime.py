"""Tests for the Home Assistant side of the catalog client (catalog_runtime.py).

The tests set up the real catalog config entry in a throw-away config folder and
replace the network client of the shared pack by a fake one: no download, and
nothing written outside `tmp_path`.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import zipfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.dispatcher import async_dispatcher_send
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.reef_maintenance import catalog_runtime as cr
from custom_components.reef_maintenance.catalog import (
    CATALOG_SPEC,
    CATALOG_UNIQUE_ID,
    CONF_CATALOG,
)
from custom_components.reef_maintenance.catalog_pack import (
    Manifest,
    PackError,
    parse_manifest,
)
from custom_components.reef_maintenance.catalog_runtime import (
    CatalogAutoUpdateSwitch,
    CatalogSpec,
    CatalogUpdateEntity,
    CatalogUpdateNowButton,
    CatalogUpdater,
)
from custom_components.reef_maintenance.const import DOMAIN

REGISTRY_KEY = f"{DOMAIN}/equipment"


# -- helpers ------------------------------------------------------------------


def make_release(
    version: str,
    items: dict[str, dict[str, Any]] | None = None,
    min_integration: dict[str, str] | None = None,
    notes: str = "",
) -> tuple[Manifest, dict[str, bytes]]:
    """A release of the equipment section and the archives of its entries."""
    entries: dict[str, Any] = {}
    blobs: dict[str, bytes] = {}
    for item_id, content in (items or {}).items():
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("item.json", json.dumps(content))
        blob = buffer.getvalue()
        name = f"item.{item_id}"
        entries[name] = {
            "kind": "item",
            "scopes": ["aquarium"],
            "sha256": hashlib.sha256(blob).hexdigest(),
            "size": len(blob),
            "archive": f"equipment-{version}/{name}.zip",
            "since": version,
        }
        blobs[name] = blob
    data = {
        "format": 1,
        "section": "equipment",
        "version": version,
        "min_integration": min_integration or {},
        "notes": notes,
        "entries": entries,
    }
    return parse_manifest(data, "equipment"), blobs


class FakeClient:
    """Stands for the PackClient of the shared pack."""

    def __init__(self) -> None:
        self.release: tuple[Manifest, dict[str, bytes]] | None = None
        self.error: Exception | None = None
        self.entry_error: Exception | None = None

    def publish(self, *args: Any, **kwargs: Any) -> Manifest:
        self.release = make_release(*args, **kwargs)
        return self.release[0]

    async def latest(self) -> Manifest:
        if self.error is not None:
            raise self.error
        assert self.release is not None
        return self.release[0]

    async def entry(self, entry: Any) -> bytes:
        if self.entry_error is not None:
            raise self.entry_error
        assert self.release is not None
        return self.release[1][entry.name]

    def release_url(self, version: str) -> str:
        return f"https://example.test/{version}"


@pytest.fixture
async def catalog(
    hass: HomeAssistant, tmp_path: Path
) -> tuple[CatalogUpdater, FakeClient]:
    """The catalog entry, set up in a private config folder, with a fake client."""
    hass.config.config_dir = str(tmp_path)
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="ReefTech equipment catalog",
        data={CONF_CATALOG: True},
        unique_id=CATALOG_UNIQUE_ID,
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    updater = cr.get_updater(hass, DOMAIN)
    assert updater is not None
    fake = FakeClient()
    updater.shared.client = fake  # type: ignore[assignment]
    return updater, fake


def fake_entry(entry_id: str | None) -> Any:
    """A stand-in for a config entry: the catalog only reads its `entry_id`."""
    return SimpleNamespace(entry_id=entry_id)


def _entity_id(hass: HomeAssistant, platform: str, unique_id: str) -> str:
    entity_id = er.async_get(hass).async_get_entity_id(platform, DOMAIN, unique_id)
    assert entity_id is not None
    return entity_id


# -- specs and registry -------------------------------------------------------


def test_spec_suffix_and_signals(hass: HomeAssistant) -> None:
    """Names of folders and signals follow the section when asked."""
    plain = CatalogSpec("d", "equipment", "T")
    by_section = CatalogSpec("d", "equipment", "T", by_section=True)
    assert plain.suffix == ""
    assert by_section.suffix == "_equipment"
    assert cr.signal_catalog_changed("d") == "d_catalog_changed"
    assert cr.signal_catalog_changed("d", "x") == "d_catalog_changed_x"
    assert cr.builtin_dir(by_section).name == "catalog_builtin_equipment"


async def test_registry_lookups(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """Updaters and shared packs are found by domain and section."""
    updater, _ = catalog
    assert cr.get_updaters(hass, DOMAIN) == [updater]
    assert cr.get_updater(hass, DOMAIN) is updater
    assert cr.get_updater(hass, DOMAIN, "equipment") is updater
    assert cr.get_updater(hass, DOMAIN, "nope") is None
    assert cr.get_updater(hass, "other") is None
    assert cr.get_shared_pack(hass, "equipment") is updater.shared
    assert cr.get_shared_pack(hass, "nope") is None
    assert updater.owner_entry_id == updater.entry_ids[0]
    assert updater.client is updater.shared.client
    assert updater.last_error == "offline (tests)"  # the first check, offline
    assert not updater.in_progress
    assert updater.progress is None
    assert updater.latest is None


async def test_owner_without_entry(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """An updater without config entry has no owner."""
    updater, _ = catalog
    saved = updater.entry_ids
    updater.entry_ids = []
    assert updater.owner_entry_id is None
    updater.entry_ids = saved


# -- shared pack: state -------------------------------------------------------


async def test_pack_state(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """`update_available` compares the release with the installed pack."""
    updater, _ = catalog
    pack = updater.shared
    pack.installed = None
    pack.latest = None
    assert not pack.update_available
    one, _ = make_release("1")
    two, _ = make_release("2")
    pack.latest = one
    assert pack.update_available  # nothing installed
    pack.installed = one
    assert not pack.update_available
    pack.latest = two
    assert pack.update_available


async def test_pack_auto_and_listeners(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """Holders choose automatic installs; listeners follow the state."""
    updater, _ = catalog
    pack = updater.shared
    assert pack.wants_auto
    pack.set_auto(DOMAIN, False)
    assert not pack.wants_auto

    calls: list[int] = []
    remove = pack.async_add_listener(lambda: calls.append(1))
    pack._notify()
    assert calls == [1]
    remove()
    pack._notify()
    assert calls == [1]


async def test_pack_stop_twice(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """Stopping the periodic checks is idempotent; a holder-less pack has no timer."""
    updater, fake = catalog
    fake.error = PackError("offline")
    pack = updater.shared
    pack.async_stop()
    pack.async_stop()
    pack.holders.clear()
    pack._schedule()
    assert pack._unsub_timer is None
    pack.holders[DOMAIN] = (True, 12)
    pack._schedule()
    assert pack._unsub_timer is not None
    await pack._async_timer(None)  # the timer only runs a check


# -- shared pack: checks and installs -----------------------------------------


async def test_check_failure_is_kept(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """A failing check never raises: the error is kept for the UI."""
    updater, fake = catalog
    fake.error = PackError("offline")
    await updater.async_check()
    assert updater.last_error == "offline"
    assert updater.shared.installed is None


async def test_check_installs_automatically(
    hass: HomeAssistant,
    catalog: tuple[CatalogUpdater, FakeClient],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """With automatic installs, a new release is downloaded and used."""
    updater, fake = catalog
    caplog.set_level(logging.INFO)
    fake.publish("1", {"fake-1": {"category": "heater", "name": {"en": "Fake"}}})
    await updater.async_check()
    pack = updater.shared
    assert pack.installed is not None and pack.installed.version == "1"
    assert (pack.root / "items" / "fake-1" / "item.json").is_file()
    assert updater.uses_shared
    assert "fake-1" in updater.view["items"]
    assert "1 entries downloaded, 0 kept" in caplog.text
    assert not updater.update_available
    assert not pack.in_progress and pack.progress is None

    # Same release again: nothing to do
    await updater.async_check()
    assert pack.installed.version == "1"

    # A new release keeps the unchanged entry and adds another
    fake.publish(
        "2",
        {
            "fake-1": {"category": "heater", "name": {"en": "Fake"}},
            "fake-2": {"category": "heater"},
        },
    )
    # `fake-1` has the same sha256 in the two releases
    old_entries = pack.installed.entries
    await updater.async_check()
    assert pack.installed.version == "2"
    assert (
        old_entries["item.fake-1"].sha256
        == pack.installed.entries["item.fake-1"].sha256
    )
    assert "fake-2" in updater.view["items"]


async def test_check_without_auto_waits_for_force(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """Without automatic installs a release is only announced."""
    updater, fake = catalog
    await updater.async_set_auto_update(False)
    fake.publish("1", {"fake-1": {"category": "heater"}})
    await updater.async_check()
    assert updater.shared.installed is None
    assert updater.update_available
    await updater.shared.async_check(force=True)
    assert updater.shared.installed is not None


async def test_install_failure_is_kept(
    hass: HomeAssistant,
    catalog: tuple[CatalogUpdater, FakeClient],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """A broken download leaves the pack as it was and keeps the error."""
    updater, fake = catalog
    fake.publish("1", {"fake-1": {"category": "heater"}})
    fake.entry_error = PackError("broken download")
    await updater.async_check()
    assert updater.last_error == "broken download"
    assert updater.shared.installed is None
    assert not updater.in_progress
    assert "catalog update failed" in caplog.text


async def test_install_guards(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """Installing needs a checked release and never runs twice at once."""
    updater, fake = catalog
    pack = updater.shared
    with pytest.raises(PackError, match="not been checked"):
        await pack.async_install()
    fake.publish("1", {"fake-1": {"category": "heater"}})
    pack.latest = fake.release[0]  # type: ignore[index]
    pack.in_progress = True
    await pack.async_install()  # already running: no-op
    assert pack.installed is None


async def test_incompatible_release_keeps_previous_pack(
    hass: HomeAssistant,
    catalog: tuple[CatalogUpdater, FakeClient],
    caplog: pytest.LogCaptureFixture,
) -> None:
    """An integration too old for a release keeps the previous pack as its own."""
    updater, fake = catalog
    fake.publish("1", {"fake-1": {"category": "heater"}})
    await updater.async_check()
    assert updater.uses_shared

    fake.publish("2", {"fake-2": {"category": "heater"}}, {DOMAIN: "999.0.0"})
    await updater.async_check()
    assert "needs" in caplog.text
    assert updater.shared.installed.version == "2"  # type: ignore[union-attr]
    assert not updater.uses_shared
    assert not updater.compatible
    assert updater.installed is not None and updater.installed.version == "1"
    assert (updater.root / "items" / "fake-1" / "item.json").is_file()
    assert "fake-2" not in updater.view["items"]
    assert "fake-1" in updater.view["items"]
    pack_layer = next(layer for layer in updater.layers() if layer.name == "pack")
    assert pack_layer.root == updater.root
    assert pack_layer.url.endswith("/pack")

    # The update entity says why it cannot install
    entity = CatalogUpdateEntity(updater)
    assert entity.release_summary is not None and "999.0.0" in entity.release_summary
    with pytest.raises(HomeAssistantError) as err:
        await updater.async_install()
    assert err.value.translation_key == "catalog_incompatible"

    # A compatible release brings the integration back on the shared pack
    fake.publish("3", {"fake-3": {"category": "heater"}})
    await updater.async_check()
    assert updater.uses_shared
    assert not updater.root.exists() or not any(updater.root.iterdir())
    assert "fake-3" in updater.view["items"]


async def test_preserve_without_previous_pack(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """The first install has no previous pack to hand over."""
    updater, _fake = catalog
    release, _ = make_release("1")
    updater.shared._preserve(None, release)
    assert not updater.root.joinpath("manifest.json").exists()


async def test_pack_layer_without_any_pack(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """Before any install the own folder is stamped with the NOT_INSTALLED version."""
    updater, _ = catalog
    layer = next(layer for layer in updater.layers() if layer.name == "pack")
    assert layer.stamp == cr.NOT_INSTALLED
    assert not updater.uses_shared
    assert updater.installed is None


# -- updater ------------------------------------------------------------------


async def test_updater_update_available(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """The updater compares the release with the pack it really uses."""
    updater, fake = catalog
    assert not updater.update_available  # nothing checked yet
    assert updater.compatible
    release = fake.publish("1")
    updater.shared.latest = release
    assert updater.update_available  # no pack at all
    updater.shared.installed = release
    assert not updater.update_available
    updater.shared.latest = make_release("2")[0]
    assert updater.update_available


async def test_updater_listeners(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """Listeners and dispatcher signals follow `notify`."""
    updater, _ = catalog
    calls: list[int] = []
    remove = updater.async_add_listener(lambda: calls.append(1))
    signals: list[int] = []
    from homeassistant.helpers.dispatcher import async_dispatcher_connect

    unsub = async_dispatcher_connect(
        hass, cr.signal_catalog_changed(DOMAIN, "equipment"), lambda: signals.append(1)
    )
    updater.notify()
    assert calls == [1] and signals == [1]
    remove()
    unsub()
    updater.notify()
    assert calls == [1]


async def test_updater_install_errors(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """The updater turns install failures into translated errors."""
    updater, fake = catalog
    with pytest.raises(HomeAssistantError) as err:
        await updater.async_install()
    assert err.value.translation_key == "catalog_unknown"

    fake.publish("1", {"fake-1": {"category": "heater"}})
    await updater.async_set_auto_update(False)
    await updater.async_check()
    fake.entry_error = PackError("nope")
    with pytest.raises(HomeAssistantError) as err:
        await updater.async_install()
    assert err.value.translation_key == "catalog_install_failed"
    assert err.value.translation_placeholders == {"error": "nope"}

    fake.entry_error = None
    await updater.async_install()
    assert updater.installed is not None


async def test_set_auto_update(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """The choice is kept in the store; turning it on checks at once."""
    updater, fake = catalog
    fake.publish("1", {"fake-1": {"category": "heater"}})
    await updater.async_set_auto_update(False)
    assert not updater.auto_update and not updater.shared.wants_auto
    assert updater.installed is None
    await updater.async_set_auto_update(True)
    assert updater.auto_update and updater.shared.wants_auto
    assert updater.installed is not None  # the check installed the release


async def test_user_layer_reload(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """A writer of the shared user layer makes the view reload."""
    updater, _ = catalog
    assert updater.user_revision == 0
    async_dispatcher_send(hass, cr.SIGNAL_USER_CATALOG_CHANGED, "supplements")
    await hass.async_block_till_done(wait_background_tasks=True)
    assert updater.user_revision == 0  # another section: ignored
    changes: list[int] = []
    updater.async_add_listener(lambda: changes.append(updater.user_revision))
    async_dispatcher_send(hass, cr.SIGNAL_USER_CATALOG_CHANGED, "equipment")
    await hass.async_block_till_done(wait_background_tasks=True)
    assert updater.user_revision == 1
    async_dispatcher_send(hass, cr.SIGNAL_USER_CATALOG_CHANGED, None)
    await hass.async_block_till_done(wait_background_tasks=True)
    assert updater.user_revision == 2
    assert changes == [1, 2]  # listeners are told once the view is rebuilt


async def test_view_cache(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """The view is built once, and again on demand."""
    updater, _ = catalog
    first = await updater.async_view()
    assert await updater.async_view() is first
    assert await updater.async_view(refresh=True) is not first
    updater._view = None
    assert updater.view == {}


# -- acquire / release --------------------------------------------------------


async def test_acquire_and_release_pack(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """Holders share a pack; the last one to leave stops it."""
    first = await cr.async_acquire_pack(hass, "parameters", "editor")
    second = await cr.async_acquire_pack(
        hass, "parameters", "other", auto=True, check_hours=1
    )
    assert second is first
    assert first.holders == {"editor": (False, 12), "other": (True, 1)}
    assert cr.get_shared_pack(hass, "parameters") is first

    cr.async_release_pack(hass, "nope", "editor")  # no such pack
    cr.async_release_pack(hass, "parameters", "stranger")  # not a holder
    cr.async_release_pack(hass, "parameters", "editor")
    assert cr.get_shared_pack(hass, "parameters") is first
    cr.async_release_pack(hass, "parameters", "other")
    assert cr.get_shared_pack(hass, "parameters") is None
    await hass.async_block_till_done()


async def test_register_pack_path(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """The pack folder is served once, and only when there is an HTTP server."""
    updater, _ = catalog
    pack = updater.shared
    registry = cr._registry(hass)
    registry.pop(f"pack_paths_{pack.section}", None)
    saved = getattr(hass, "http", None)

    hass.http = None  # type: ignore[assignment]
    await cr._async_register_pack_path(hass, pack)
    assert f"pack_paths_{pack.section}" not in registry

    hass.http = SimpleNamespace(async_register_static_paths=AsyncMock())  # type: ignore[assignment]
    await cr._async_register_pack_path(hass, pack)
    await cr._async_register_pack_path(hass, pack)  # already done: no second call
    hass.http.async_register_static_paths.assert_awaited_once()  # type: ignore[attr-defined]
    hass.http = saved  # type: ignore[assignment]


async def test_register_paths(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """The folders of the domain are served once, and only when they exist."""
    updater, _ = catalog
    key = f"paths_{DOMAIN}{updater.spec.suffix}"
    registry = cr._registry(hass)
    registry.pop(key, None)
    saved = getattr(hass, "http", None)

    hass.http = None  # type: ignore[assignment]
    await cr._async_register_paths(hass, updater)
    assert key not in registry

    hass.http = SimpleNamespace(async_register_static_paths=AsyncMock())  # type: ignore[assignment]
    await cr._async_register_paths(hass, updater)
    await cr._async_register_paths(hass, updater)
    hass.http.async_register_static_paths.assert_awaited_once()  # type: ignore[attr-defined]
    configs = hass.http.async_register_static_paths.await_args.args[0]  # type: ignore[attr-defined]
    assert next(c.url_path for c in configs).endswith("/builtin")
    hass.http = saved  # type: ignore[assignment]


async def test_unload_catalog(
    hass: HomeAssistant,
    catalog: tuple[CatalogUpdater, FakeClient],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Forgetting an entry stops the updater with the last one."""
    updater, _ = catalog
    owner = updater.owner_entry_id
    assert owner is not None

    # Unknown section, unknown entry: nothing happens
    await cr.async_unload_catalog(
        hass,
        fake_entry(owner),
        CatalogSpec(DOMAIN, "nope", "x"),  # type: ignore[arg-type]
    )
    await cr.async_unload_catalog(hass, fake_entry("zzz"), CATALOG_SPEC)  # type: ignore[arg-type]
    assert cr.get_updater(hass, DOMAIN) is updater

    # The owner leaves while another entry stays: the next one is reloaded
    reload = MagicMock()
    monkeypatch.setattr(hass.config_entries, "async_schedule_reload", reload)
    updater.entry_ids.append("second")
    await cr.async_unload_catalog(hass, fake_entry(owner), CATALOG_SPEC)  # type: ignore[arg-type]
    reload.assert_called_once_with("second")
    assert cr.get_updater(hass, DOMAIN) is updater

    # A non-owner leaves: nothing to reload
    reload.reset_mock()
    updater.entry_ids.append("third")
    await cr.async_unload_catalog(hass, fake_entry("third"), CATALOG_SPEC)  # type: ignore[arg-type]
    reload.assert_not_called()

    # The last one leaves: the updater stops
    await cr.async_unload_catalog(hass, fake_entry("second"), CATALOG_SPEC)  # type: ignore[arg-type]
    assert cr.get_updater(hass, DOMAIN) is None
    assert cr.get_shared_pack(hass, "equipment") is None


async def test_setup_registers_second_entry(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """A second entry joins the running updater (and is not added twice)."""
    updater, _ = catalog
    other = fake_entry("other-entry")
    assert await cr.async_setup_catalog(hass, other, CATALOG_SPEC) is updater  # type: ignore[arg-type]
    assert await cr.async_setup_catalog(hass, other, CATALOG_SPEC) is updater  # type: ignore[arg-type]
    assert updater.entry_ids.count("other-entry") == 1
    updater.entry_ids.remove("other-entry")


# -- websocket ----------------------------------------------------------------


async def test_ws_catalog(
    hass: HomeAssistant, hass_ws_client: Any, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """The merged catalog is served, whole or refreshed."""
    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/catalog"})
    result = (await client.receive_json())["result"]
    assert result["section"] == "equipment"
    assert result["version"] is None
    assert result["updating"] is False
    assert "heater" in result["data"]["categories"]

    await client.send_json(
        {"id": 2, "type": f"{DOMAIN}/catalog", "refresh": True, "section": "equipment"}
    )
    assert (await client.receive_json())["success"]

    updater, fake = catalog
    fake.publish("1", {"fake-1": {"category": "heater"}})
    await updater.async_check()
    await client.send_json({"id": 3, "type": f"{DOMAIN}/catalog"})
    assert (await client.receive_json())["result"]["version"] == "1"

    await client.send_json({"id": 4, "type": f"{DOMAIN}/catalog", "section": "nope"})
    response = await client.receive_json()
    assert not response["success"]
    assert response["error"]["code"] == "not_loaded"
    assert "nope" in response["error"]["message"]


async def test_ws_catalog_not_loaded(
    hass: HomeAssistant, hass_ws_client: Any, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """Without a running updater every command answers `not_loaded`."""
    client = await hass_ws_client(hass)
    registry = cr._registry(hass)
    updater = registry.pop(REGISTRY_KEY)
    try:
        for index, message in enumerate(
            (
                {"type": f"{DOMAIN}/catalog"},
                {"type": f"{DOMAIN}/catalog/subscribe"},
                {"type": f"{DOMAIN}/catalog/maintenance", "item_id": "x"},
            ),
            start=1,
        ):
            await client.send_json({"id": index, **message})
            response = await client.receive_json()
            assert response["error"]["code"] == "not_loaded"
            assert "catalog" in response["error"]["message"] or (
                "equipment" in response["error"]["message"]
            )
    finally:
        registry[REGISTRY_KEY] = updater


async def test_ws_subscribe(
    hass: HomeAssistant, hass_ws_client: Any, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """A subscriber gets the state at once, then each change (not repeats)."""
    updater, fake = catalog
    client = await hass_ws_client(hass)
    await client.send_json({"id": 1, "type": f"{DOMAIN}/catalog/subscribe"})
    assert (await client.receive_json())["success"]
    first = await client.receive_json()
    assert first["event"] == {"version": None, "updating": False}

    updater.notify()  # same state: no event
    fake.publish("1", {"fake-1": {"category": "heater"}})
    await updater.async_check()
    await hass.async_block_till_done()
    # The install went through "updating" then to the new version
    events = []
    while True:
        message = await client.receive_json()
        events.append(message["event"])
        if message["event"]["version"] == "1" and not message["event"]["updating"]:
            break
    assert {"version": None, "updating": True} in events

    await client.send_json({"id": 2, "type": "unsubscribe_events", "subscription": 1})
    assert (await client.receive_json())["success"]


async def test_ws_maintenance(
    hass: HomeAssistant, hass_ws_client: Any, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """The tasks an equipment would get are resolved from the view."""
    client = await hass_ws_client(hass)
    await client.send_json(
        {
            "id": 1,
            "type": f"{DOMAIN}/catalog/maintenance",
            "item_id": "tunze-turbelle-stream",
        }
    )
    response = await client.receive_json()
    assert response["success"]
    assert response["result"]["tasks"]

    await client.send_json(
        {"id": 2, "type": f"{DOMAIN}/catalog/maintenance", "category_id": "heater"}
    )
    assert (await client.receive_json())["result"]["tasks"]


async def test_register_commands_once(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """Registering the commands again does nothing."""
    registry = cr._registry(hass)
    assert registry[f"websocket_{DOMAIN}"] is True
    assert registry[f"websocket_maintenance_{DOMAIN}"] is True
    cr._register_websocket(hass, DOMAIN)
    cr._register_maintenance_command(hass, DOMAIN)


# -- entities -----------------------------------------------------------------


async def test_catalog_entities(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """Entities are created for the hosting entry only, per platform."""
    updater, _ = catalog
    owner = fake_entry(updater.owner_entry_id)
    other = fake_entry("not-the-owner")

    def kinds(entry: Any, platform: str) -> list[type]:
        return [type(e) for e in cr.catalog_entities(hass, entry, DOMAIN, platform)]  # type: ignore[arg-type]

    assert kinds(owner, "update") == [CatalogUpdateEntity]
    assert kinds(owner, "switch") == [CatalogAutoUpdateSwitch]
    assert kinds(owner, "button") == [CatalogUpdateNowButton]
    assert kinds(owner, "sensor") == []
    for platform in ("update", "switch", "button"):
        assert kinds(other, platform) == []


async def test_second_section_entities(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """A second section gets its own update entity, named after the section."""
    updater, _ = catalog
    spec = CatalogSpec(DOMAIN, "parameters", "Parameters", by_section=True)
    shared = await cr.async_acquire_pack(hass, "parameters", DOMAIN)
    second = CatalogUpdater(hass, spec, "1.0", shared)
    cr._registry(hass)[f"{DOMAIN}/parameters"] = second
    second.entry_ids.append("second-entry")
    try:
        entry = fake_entry("second-entry")
        (entity,) = cr.catalog_entities(hass, entry, DOMAIN, "update")  # type: ignore[arg-type]
        assert entity.name == "Parameters"  # device is named after the first section
        # The domain-wide entities belong to its first section only
        assert cr.catalog_entities(hass, entry, DOMAIN, "switch") == []  # type: ignore[arg-type]
        assert second.layers()[0].name != "builtin"  # no snapshot for this section
        assert any(u is second for u in cr.get_updaters(hass, DOMAIN))
    finally:
        del cr._registry(hass)[f"{DOMAIN}/parameters"]
        cr.async_release_pack(hass, "parameters", DOMAIN)
        second.shared.updaters.pop(DOMAIN, None)
        assert updater is cr.get_updater(hass, DOMAIN)


async def test_update_entity(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """The update entity follows the release, notes and installs on demand."""
    updater, fake = catalog
    entity = CatalogUpdateEntity(updater)
    assert entity.name is None  # named after its device
    assert entity.installed_version == cr.NOT_INSTALLED
    assert entity.latest_version == cr.NOT_INSTALLED
    assert entity.release_url is None
    assert entity.release_summary is None
    assert await entity.async_release_notes() is None

    await updater.async_set_auto_update(False)
    fake.publish("1", {"fake-1": {"category": "heater"}}, notes="# notes")
    await entity.async_update()  # a check
    entity._refresh()
    assert entity.latest_version == "1"
    assert entity.release_url == "https://example.test/1"
    assert await entity.async_release_notes() == "# notes"

    await entity.async_install(None, False)
    entity._refresh()
    assert entity.installed_version == "1"
    assert entity.latest_version == "1"

    fake.publish("2")  # no notes
    await entity.async_update()
    assert await entity.async_release_notes() is None


async def test_update_entity_service(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """The entity registered by the platform shows the state and can install."""
    updater, fake = catalog
    entity_id = _entity_id(hass, "update", "catalog_equipment")
    assert hass.states.get(entity_id).state == "off"  # type: ignore[union-attr]
    await updater.async_set_auto_update(False)
    fake.publish("1", {"fake-1": {"category": "heater"}})
    await updater.async_check()
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == "on"  # type: ignore[union-attr]
    await hass.services.async_call(
        "update", "install", {"entity_id": entity_id}, blocking=True
    )
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == "off"  # type: ignore[union-attr]


async def test_auto_update_switch(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """The switch turns automatic installs on and off."""
    updater, fake = catalog
    fake.error = PackError("offline")  # turning it on checks at once
    entity_id = _entity_id(hass, "switch", "catalog_equipment_auto_update")
    assert hass.states.get(entity_id).state == "on"  # type: ignore[union-attr]
    await hass.services.async_call(
        "switch", "turn_off", {"entity_id": entity_id}, blocking=True
    )
    assert not updater.auto_update
    assert hass.states.get(entity_id).state == "off"  # type: ignore[union-attr]
    await hass.services.async_call(
        "switch", "turn_on", {"entity_id": entity_id}, blocking=True
    )
    assert updater.auto_update
    assert hass.states.get(entity_id).state == "on"  # type: ignore[union-attr]


async def test_update_now_button(
    hass: HomeAssistant, catalog: tuple[CatalogUpdater, FakeClient]
) -> None:
    """The button checks then installs, and reports a failing check."""
    updater, fake = catalog
    entity_id = _entity_id(hass, "button", "catalog_equipment_update_now")

    fake.error = PackError("offline")
    with pytest.raises(HomeAssistantError) as err:
        await hass.services.async_call(
            "button", "press", {"entity_id": entity_id}, blocking=True
        )
    assert err.value.translation_key == "catalog_check_failed"

    fake.error = None
    await updater.async_set_auto_update(False)
    fake.publish("1", {"fake-1": {"category": "heater"}})
    await hass.services.async_call(
        "button", "press", {"entity_id": entity_id}, blocking=True
    )
    assert updater.installed is not None and updater.installed.version == "1"

    # Nothing new: the check goes through without installing
    await hass.services.async_call(
        "button", "press", {"entity_id": entity_id}, blocking=True
    )
