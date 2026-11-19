"""Tests for the catalog client (manifest, packs on disk, network, merged view)."""

from __future__ import annotations

import hashlib
import io
import json
import logging
import zipfile
from pathlib import Path
from typing import Any, Self

import aiohttp
import pytest

from custom_components.reef_maintenance import catalog_pack as cp
from custom_components.reef_maintenance.catalog_pack import (
    Layer,
    Manifest,
    PackClient,
    PackEntry,
    PackError,
)

SHA = "a" * 64

# The autouse fixture of conftest.py replaces `PackClient.latest` by a failure:
# keep the real one, captured at import time, for the tests of the client itself.
_REAL_LATEST = PackClient.latest


def _record(
    kind: str = "item", archive: Any = "equipment-1.0/item.x.zip", **extra: Any
) -> dict[str, Any]:
    """One manifest record, valid by default."""
    return {
        "kind": kind,
        "sha256": SHA,
        "size": 10,
        "archive": archive,
        "since": "1.0",
        **extra,
    }


def _manifest_data(**extra: Any) -> dict[str, Any]:
    data: dict[str, Any] = {
        "format": 1,
        "section": "equipment",
        "version": "1.0",
        "entries": {"item.pump-1": _record()},
    }
    data.update(extra)
    return data


def _zip(files: dict[str, bytes | str]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return buffer.getvalue()


def _entry(kind: str = "item", name: str = "item.pump-1", size: int = 10) -> PackEntry:
    return PackEntry(name, kind, SHA, size, "equipment-1.0/x.zip", "1.0")


# -- PackEntry ----------------------------------------------------------------


def test_entry_id_and_rel_dir() -> None:
    """The id is the part after the kind; the task library has no id."""
    assert _entry().entry_id == "pump-1"
    assert str(_entry().rel_dir) == "items/pump-1"
    tasks = _entry(kind="tasks", name="tasks")
    assert tasks.entry_id == "tasks"
    assert str(tasks.rel_dir) == "tasks"


def test_shared_parts() -> None:
    """Shared folders are named after the section."""
    assert cp.shared_user_parts("equipment") == (
        "reeftech_catalog",
        "user",
        "equipment",
    )
    assert cp.shared_pack_parts("equipment") == (
        "reeftech_catalog",
        "pack",
        "equipment",
    )


# -- manifest -----------------------------------------------------------------


def test_parse_manifest_ok() -> None:
    """A valid manifest is parsed, with scopes and schema."""
    data = _manifest_data(
        min_integration={"reef_maintenance": "0.3.0"},
        notes="hello",
        schema=_record(kind="schema", archive="equipment-1.0/schema.zip"),
    )
    data["entries"]["item.pump-1"]["scopes"] = ["aquarium"]
    data["entries"]["tasks"] = _record(kind="tasks")
    manifest = cp.parse_manifest(data, "equipment")
    assert manifest.version == "1.0"
    assert manifest.notes == "hello"
    assert manifest.entries["item.pump-1"].scopes == ("aquarium",)
    assert manifest.entries["tasks"].scopes is None
    assert manifest.schema is not None
    assert manifest.schema.kind == "schema"


@pytest.mark.parametrize(
    ("data", "section", "message"),
    [
        (_manifest_data(), "nope", "unknown section"),
        ([], "equipment", "not an object"),
        (_manifest_data(format=2), "equipment", "unsupported manifest format"),
        (_manifest_data(section="supplements"), "equipment", "expected"),
        (_manifest_data(version="bad version!"), "equipment", "bad manifest version"),
        (_manifest_data(min_integration=[]), "equipment", "must be an object"),
        (
            _manifest_data(min_integration={"x": "bad version!"}),
            "equipment",
            "min_integration of x",
        ),
        (_manifest_data(notes=3), "equipment", "notes must be a text"),
        (_manifest_data(entries=[]), "equipment", "entries must be an object"),
        (_manifest_data(schema=[]), "equipment", "schema is not an object"),
    ],
)
def test_parse_manifest_errors(data: Any, section: str, message: str) -> None:
    """Every malformed manifest is refused with a PackError."""
    with pytest.raises(PackError, match=message):
        cp.parse_manifest(data, section)


@pytest.mark.parametrize(
    ("name", "item", "message"),
    [
        ("item.x", 3, "is not an object"),
        ("item.x", _record(kind="supplement"), "not in section"),
        ("other", _record(kind="tasks"), "bad entry name"),
        ("category.x", _record(kind="item"), "bad entry name"),
        ("item.Bad Id", _record(), "bad entry name"),
        ("item.x", _record(sha256="zz"), "bad sha256"),
        ("item.x", _record(sha256=3), "bad sha256"),
        ("item.x", _record(size=0), "bad size"),
        ("item.x", _record(size=True), "bad size"),
        ("item.x", _record(size="3"), "bad size"),
        ("item.x", _record(size=10**9), "bad size"),
        ("item.x", _record(archive=3), "bad archive"),
        ("item.x", _record(archive="../x.zip"), "bad archive"),
        ("item.x", _record(archive="supplements-1.0/x.zip"), "bad archive"),
        ("item.x", _record(since="bad version!"), "version"),
        ("item.x", _record(scopes="aquarium"), "bad scopes"),
        ("item.x", _record(scopes=[1]), "bad scopes"),
    ],
)
def test_parse_entry_errors(name: str, item: Any, message: str) -> None:
    """Every malformed entry is refused with a PackError."""
    with pytest.raises(PackError, match=message):
        cp._parse_entry(name, item, "equipment")


# -- select / compatibility ---------------------------------------------------


def test_select_scopes() -> None:
    """`select` keeps the entries without scopes and the wanted ones."""
    data = _manifest_data()
    data["entries"]["item.pool-1"] = _record(scopes=["pool"])
    data["entries"]["item.reef-1"] = _record(scopes=["aquarium"])
    data["entries"]["tasks"] = _record(kind="tasks")
    manifest = cp.parse_manifest(data, "equipment")

    assert cp.select(manifest, None) is manifest
    kept = cp.select(manifest, ["aquarium"])
    assert set(kept.entries) == {"item.pump-1", "item.reef-1", "tasks"}
    assert "item.pool-1" not in kept.entries
    assert set(kept.raw["entries"]) == set(kept.entries)


def test_is_compatible() -> None:
    """Compatibility follows min_integration, and tolerates a leading v."""
    manifest = Manifest("equipment", "1.0", {"reef": "v1.2.0"})
    assert cp.is_compatible(manifest, "other", "0.0.1")  # no minimum for it
    assert cp.is_compatible(manifest, "reef", "v1.2.0")
    assert cp.is_compatible(manifest, "reef", "2.0.0")
    assert not cp.is_compatible(manifest, "reef", "1.1.0")


def test_is_compatible_unparsable(monkeypatch: pytest.MonkeyPatch) -> None:
    """A version that cannot be compared is not compatible."""

    def boom(_value: str) -> None:
        raise cp.AwesomeVersionException("nope")

    monkeypatch.setattr(cp, "AwesomeVersion", boom)
    manifest = Manifest("equipment", "1.0", {"reef": "1.0.0"})
    assert not cp.is_compatible(manifest, "reef", "1.0.0")


# -- installed pack -----------------------------------------------------------


def _install(root: Path, manifest_data: dict[str, Any], files: dict[str, str]) -> None:
    root.mkdir(parents=True)
    (root / "manifest.json").write_text(json.dumps(manifest_data), encoding="utf-8")
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def test_read_installed(tmp_path: Path) -> None:
    """A complete pack is read back; a missing entry or manifest gives None."""
    data = _manifest_data()
    data["entries"]["tasks"] = _record(kind="tasks")
    root = tmp_path / "pack"
    _install(
        root,
        data,
        {"items/pump-1/item.json": "{}", "tasks/a.json": "{}"},
    )
    manifest = cp.read_installed(root, "equipment")
    assert manifest is not None
    assert set(manifest.entries) == {"item.pump-1", "tasks"}

    (root / "tasks" / "a.json").unlink()
    assert cp.read_installed(root, "equipment") is None  # tasks folder empty

    (root / "items" / "pump-1" / "item.json").unlink()
    assert cp.read_installed(root, "equipment") is None  # descriptor missing

    assert cp.read_installed(tmp_path / "absent", "equipment") is None

    (root / "manifest.json").write_text("not json", encoding="utf-8")
    assert cp.read_installed(root, "equipment") is None

    (root / "manifest.json").write_text("{}", encoding="utf-8")
    assert cp.read_installed(root, "equipment") is None  # PackError


def test_plan() -> None:
    """Unchanged entries are kept, new or changed ones are fetched."""
    data = _manifest_data()
    data["entries"]["item.pump-2"] = _record()
    latest = cp.parse_manifest(data, "equipment")

    old_data = _manifest_data()
    old_data["entries"]["item.pump-2"] = _record(sha256="b" * 64)
    installed = cp.parse_manifest(old_data, "equipment")

    keep, fetch = cp.plan(installed, latest)
    assert [e.name for e in keep] == ["item.pump-1"]
    assert [e.name for e in fetch] == ["item.pump-2"]

    keep, fetch = cp.plan(None, latest)
    assert keep == []
    assert [e.name for e in fetch] == ["item.pump-1", "item.pump-2"]


# -- verify / extract ---------------------------------------------------------


def test_verify() -> None:
    """Size and checksum are both checked."""
    blob = b"hello"
    good = PackEntry("item.x", "item", hashlib.sha256(blob).hexdigest(), 5, "a", "1.0")
    cp.verify(blob, good)
    with pytest.raises(PackError, match="expected 5"):
        cp.verify(b"hell", good)
    with pytest.raises(PackError, match="checksum"):
        cp.verify(b"hellp", good)


def test_extract_ok(tmp_path: Path) -> None:
    """A valid archive is extracted flat."""
    blob = _zip({"item.json": "{}", "image.webp": b"img"})
    dest = tmp_path / "out"
    cp.extract_entry(blob, _entry(), dest)
    assert (dest / "item.json").read_text() == "{}"
    assert (dest / "image.webp").read_bytes() == b"img"


def test_extract_schema_has_no_descriptor(tmp_path: Path) -> None:
    """The schema archive holds only JSON files, no descriptor."""
    blob = _zip({"a.json": "{}"})
    cp.extract_entry(blob, _entry(kind="schema", name="schema"), tmp_path / "s")
    assert (tmp_path / "s" / "a.json").is_file()


def test_extract_skips_non_json_parse(tmp_path: Path) -> None:
    """Images are not parsed as JSON."""
    blob = _zip({"item.json": "{}", "thumb.webp": b"\x00\xff"})
    cp.extract_entry(blob, _entry(), tmp_path / "o")


@pytest.mark.parametrize(
    ("files", "message"),
    [
        ({}, "0 files"),
        ({"sub/item.json": "{}"}, "unexpected file"),
        ({"bad name.json": "{}"}, "unexpected file"),
        ({"item.txt": "x"}, "unexpected file"),
        ({"image.webp": b"x"}, "no item.json"),
        ({"item.json": b"\xff\xfe"}, "unreadable"),
        ({"item.json": "{bad"}, "unreadable"),
        ({"item.json": "[]"}, "is not an object"),
    ],
)
def test_extract_errors(tmp_path: Path, files: dict[str, Any], message: str) -> None:
    """Every unusable archive is refused."""
    with pytest.raises(PackError, match=message):
        cp.extract_entry(_zip(files), _entry(), tmp_path / "o")


def test_extract_not_a_zip(tmp_path: Path) -> None:
    """A blob that is not a zip is refused."""
    with pytest.raises(PackError, match="not a zip"):
        cp.extract_entry(b"nope", _entry(), tmp_path / "o")


def test_extract_too_many_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An archive with too many files is refused."""
    monkeypatch.setattr(cp, "MAX_ENTRY_FILES", 1)
    blob = _zip({"item.json": "{}", "image.webp": b"x"})
    with pytest.raises(PackError, match="2 files"):
        cp.extract_entry(blob, _entry(), tmp_path / "o")


def test_extract_too_big(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An archive that is too big once extracted is refused."""
    monkeypatch.setattr(cp, "MAX_ENTRY_BYTES", 1)
    blob = _zip({"item.json": "{}" + " " * 10})
    with pytest.raises(PackError, match="too big once extracted"):
        cp.extract_entry(blob, _entry(), tmp_path / "o")


# -- staging / commit / copy --------------------------------------------------


def test_staging_commit(tmp_path: Path) -> None:
    """Kept entries are copied to a fresh staging folder, then swapped in."""
    root = tmp_path / "pack"
    (root / "items" / "pump-1").mkdir(parents=True)
    (root / "items" / "pump-1" / "item.json").write_text("{}")
    stale = tmp_path / "pack.new"
    stale.mkdir()
    (stale / "junk").write_text("x")
    (tmp_path / "pack.old").mkdir()

    staging = cp.prepare_staging(root, [_entry()])
    assert staging == cp.staging_dir(root) == tmp_path / "pack.new"
    assert not (staging / "junk").exists()
    assert (staging / "items" / "pump-1" / "item.json").is_file()

    manifest = cp.parse_manifest(_manifest_data(), "equipment")
    cp.commit(root, staging, manifest)
    assert json.loads((root / "manifest.json").read_text())["version"] == "1.0"
    assert (root / "items" / "pump-1" / "item.json").is_file()
    assert not staging.exists()
    assert not (tmp_path / "pack.old").exists()


def test_commit_without_existing_pack(tmp_path: Path) -> None:
    """The first install has no previous pack to move away."""
    root = tmp_path / "pack"
    staging = cp.prepare_staging(root, [])
    cp.commit(root, staging, cp.parse_manifest(_manifest_data(), "equipment"))
    assert (root / "manifest.json").is_file()


def test_copy_pack(tmp_path: Path) -> None:
    """The destination is replaced by a copy of the source, atomically."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.json").write_text("new")
    dest = tmp_path / "deep" / "dest"
    cp.copy_pack(src, dest)  # destination does not exist yet
    assert (dest / "a.json").read_text() == "new"

    (src / "a.json").write_text("newer")
    (tmp_path / "deep" / "dest.new").mkdir()
    (tmp_path / "deep" / "dest.old").mkdir()
    cp.copy_pack(src, dest)  # replaces an existing destination
    assert (dest / "a.json").read_text() == "newer"
    assert not (tmp_path / "deep" / "dest.old").exists()


# -- network ------------------------------------------------------------------


class _Content:
    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = chunks

    async def iter_chunked(self, _size: int):
        for chunk in self._chunks:
            yield chunk


class _Response:
    def __init__(self, status: int = 200, chunks: list[bytes] | None = None) -> None:
        self.status = status
        self.content = _Content(chunks or [])

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        return None


class _Session:
    def __init__(self, response: _Response | Exception) -> None:
        self._response = response
        self.urls: list[str] = []

    def get(self, url: str, timeout: Any = None) -> _Response:
        self.urls.append(url)
        if isinstance(self._response, Exception):
            raise self._response
        return self._response


async def test_download_ok() -> None:
    """The body is the concatenation of the chunks."""
    session = _Session(_Response(chunks=[b"ab", b"cd"]))
    assert await cp.download(session, "http://x", 10) == b"abcd"  # type: ignore[arg-type]


async def test_download_errors() -> None:
    """HTTP errors, oversized bodies and network errors become PackError."""
    with pytest.raises(PackError, match="HTTP 404"):
        await cp.download(_Session(_Response(status=404)), "http://x", 10)  # type: ignore[arg-type]
    with pytest.raises(PackError, match="more than 3 bytes"):
        await cp.download(_Session(_Response(chunks=[b"abcd"])), "http://x", 3)  # type: ignore[arg-type]
    with pytest.raises(PackError, match="boom"):
        await cp.download(_Session(aiohttp.ClientError("boom")), "http://x", 3)  # type: ignore[arg-type]
    with pytest.raises(PackError):
        await cp.download(_Session(TimeoutError("slow")), "http://x", 3)  # type: ignore[arg-type]


async def test_pack_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """The client builds its URLs, reads the manifest and checked archives."""
    monkeypatch.setattr(PackClient, "latest", _REAL_LATEST)
    manifest_blob = json.dumps(_manifest_data()).encode()
    session = _Session(_Response(chunks=[manifest_blob]))
    client = PackClient(session, "equipment", repo="o/r")  # type: ignore[arg-type]
    assert client.manifest_url == (
        "https://github.com/o/r/releases/download/equipment-latest/manifest.json"
    )
    assert (
        client.release_url("1.0") == "https://github.com/o/r/releases/tag/equipment-1.0"
    )
    manifest = await client.latest()
    assert manifest.version == "1.0"

    blob = b"payload"
    entry = PackEntry(
        "item.x",
        "item",
        hashlib.sha256(blob).hexdigest(),
        len(blob),
        "equipment-1.0/x.zip",
        "1.0",
    )
    client = PackClient(_Session(_Response(chunks=[blob])), "equipment")  # type: ignore[arg-type]
    assert await client.entry(entry) == blob


async def test_pack_client_unreadable_manifest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A manifest that is not UTF-8 JSON is refused."""
    monkeypatch.setattr(PackClient, "latest", _REAL_LATEST)
    for body in (b"\xff\xfe", b"{bad"):
        client = PackClient(_Session(_Response(chunks=[body])), "equipment")  # type: ignore[arg-type]
        with pytest.raises(PackError, match="unreadable manifest"):
            await client.latest()


# -- merged view --------------------------------------------------------------


def _layer(root: Path, name: str = "builtin") -> Layer:
    return Layer(name, root, f"/static/{name}", "s1")


def _write(root: Path, rel: str, data: Any) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data if isinstance(data, str) else json.dumps(data))


def test_read_object(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """Unreadable, oversized and non-object files are ignored with a warning."""
    good = tmp_path / "good.json"
    good.write_text('{"a": 1}')
    assert cp._read_object(good) == {"a": 1}

    caplog.set_level(logging.WARNING)
    assert cp._read_object(tmp_path / "missing.json") is None
    bad = tmp_path / "bad.json"
    bad.write_text("{bad")
    assert cp._read_object(bad) is None
    arr = tmp_path / "arr.json"
    arr.write_text("[]")
    assert cp._read_object(arr) is None
    assert "not an object" in caplog.text


def test_read_object_too_big(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A file over the size limit is ignored."""
    monkeypatch.setattr(cp, "MAX_JSON_BYTES", 1)
    path = tmp_path / "big.json"
    path.write_text('{"a": 1}')
    assert cp._read_object(path) is None


def test_with_files(tmp_path: Path) -> None:
    """Image and thumbnail URLs follow the files present; thumb falls back."""
    layer = _layer(tmp_path)
    folder = tmp_path / "items" / "x"
    folder.mkdir(parents=True)
    bare = cp._with_files({"a": 1}, folder, layer, "items/x")
    assert bare["image"] is None
    assert bare["thumb"] is None
    assert bare["source"] == "builtin"

    (folder / "image.png").write_bytes(b"x")
    only_image = cp._with_files({}, folder, layer, "items/x")
    assert only_image["image"] == "/static/builtin/items/x/image.png?v=s1"
    assert only_image["thumb"] == only_image["image"]

    (folder / "thumb.webp").write_bytes(b"x")
    both = cp._with_files({}, folder, layer, "items/x")
    assert both["thumb"] == "/static/builtin/items/x/thumb.webp?v=s1"


def _equipment_root(root: Path) -> None:
    _write(root, "tasks/clean.json", {"name": {"en": "Clean"}})
    _write(root, "tasks/Bad Name.json", {})
    _write(root, "tasks/broken.json", "{bad")
    _write(root, "categories/heater/category.json", {"scopes": ["aquarium"]})
    _write(root, "categories/pool/category.json", {"scopes": ["pool"]})
    _write(root, "categories/nodesc/readme.txt", "x")  # no descriptor
    _write(root, "items/h1/item.json", {"category": "heater"})
    _write(root, "items/p1/item.json", {"category": "pool"})
    _write(root, "items/orphan/item.json", {"category": "unknown"})
    _write(root, "items/h2/item.json", {"category": "heater", "scopes": ["pool"]})
    _write(root, "items/Bad Id/item.json", {"category": "heater"})
    (root / "items" / "stray.txt").write_text("x")  # a file, not a folder


def test_read_layer(tmp_path: Path) -> None:
    """A layer is read by group, skipping what is not an entry."""
    _equipment_root(tmp_path)
    groups = cp.read_layer(_layer(tmp_path), "equipment")
    assert set(groups["tasks"]) == {"clean"}
    assert set(groups["categories"]) == {"heater", "pool"}
    assert set(groups["items"]) == {"h1", "p1", "orphan", "h2"}


def test_read_layer_empty(tmp_path: Path) -> None:
    """A layer without folders gives empty groups; other sections have no tasks."""
    groups = cp.read_layer(_layer(tmp_path), "equipment")
    assert groups == {"tasks": {}, "categories": {}, "items": {}}
    assert cp.read_layer(_layer(tmp_path), "supplements") == {"items": {}}


def test_build_view(tmp_path: Path) -> None:
    """Later layers win; scopes filter; orphan items are dropped."""
    base = tmp_path / "base"
    user = tmp_path / "user"
    _equipment_root(base)
    _write(user, "tasks/clean.json", {"name": {"en": "Mine"}})

    view = cp.build_view([_layer(base), _layer(user, "user")], "equipment")
    assert view["tasks"]["clean"]["name"] == {"en": "Mine"}
    assert set(view["items"]) == {"h1", "p1", "h2"}  # orphan dropped
    assert view["items"]["h1"]["scopes"] == ["aquarium"]  # from its category

    scoped = cp.build_view([_layer(base)], "equipment", scopes=["aquarium"])
    assert set(scoped["categories"]) == {"heater"}
    assert set(scoped["items"]) == {"h1"}  # h2 has its own scope: pool


def test_build_view_other_section(tmp_path: Path) -> None:
    """Sections other than equipment are returned as read."""
    _write(tmp_path, "items/s1/supplement.json", {"name": "x"})
    view = cp.build_view([_layer(tmp_path)], "supplements")
    assert set(view["items"]) == {"s1"}


def test_in_scopes() -> None:
    """Entries without a list of scopes are always in scope."""
    assert cp._in_scopes({}, {"a"})
    assert cp._in_scopes({"scopes": ["a"]}, None)
    assert cp._in_scopes({"scopes": ["a"]}, {"a"})
    assert not cp._in_scopes({"scopes": ["a"]}, {"b"})
    assert cp._in_scopes({"scopes": "a"}, {"b"})


def test_usable_icon() -> None:
    """Icons of an unavailable set are dropped."""
    assert cp.usable_icon("mdi:wrench") == "mdi:wrench"
    assert cp.usable_icon("redsea:x") is None
    assert cp.usable_icon("redsea:x", ("mdi", "redsea")) == "redsea:x"
    assert cp.usable_icon("nocolon") is None
    assert cp.usable_icon(3) is None


def test_resolve_maintenance() -> None:
    """Category tasks are overridden by item tasks; unknown ones are skipped."""
    view = {
        "tasks": {
            "clean": {
                "name": {"en": "Clean"},
                "icon": "mdi:wrench",
                "schedule": {"every": 1},
            },
            "test": {"regulatory": True},
        },
        "categories": {
            "heater": {
                "maintenance": [
                    {"task": "clean"},
                    {"task": "ghost"},
                    "not a dict",
                ]
            }
        },
        "items": {
            "h1": {
                "category": "heater",
                "maintenance": [
                    {"task": "clean", "schedule": {"every": 2}},
                    {"task": "test"},
                    "not a dict",
                ],
            },
            "h2": {"category": "heater", "inherit_maintenance": False},
        },
    }
    by_item = {t["task"]: t for t in cp.resolve_maintenance(view, item_id="h1")}
    assert set(by_item) == {"clean", "test"}
    assert by_item["clean"]["schedule"] == {"every": 2}
    assert by_item["clean"]["icon"] == "mdi:wrench"
    assert by_item["test"]["regulatory"] is True
    assert by_item["test"]["name"] == {}

    assert cp.resolve_maintenance(view, item_id="h2") == []
    by_category = cp.resolve_maintenance(view, category_id="heater")
    assert [t["task"] for t in by_category] == ["clean"]
    assert by_category[0]["schedule"] == {"every": 1}
    assert by_category[0]["regulatory"] is False
    assert cp.resolve_maintenance(view) == []
