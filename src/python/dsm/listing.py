"""Directory listings: the snapshot a reader walks (DirectoryListing.schema.json)."""
import json
import os
import pathlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

import jsonschema

from .errors import ListingError
from .schemas import LISTING_SCHEMA, load_schema


@dataclass
class Root:
    data_location: str
    root_storage_path: str
    entries: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"dataLocationIdentifier": self.data_location,
                "rootStoragePathIdentifier": self.root_storage_path,
                "entries": list(self.entries)}


@dataclass
class Listing:
    roots: List[Root]
    environment: Optional[str] = None

    def to_dict(self) -> dict:
        doc = {"roots": [r.to_dict() for r in self.roots]}
        if self.environment is not None:
            doc = {"environmentIdentifier": self.environment, **doc}
        return doc

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2) + "\n"


def is_dir(entry: str) -> bool:
    return entry.endswith("/")


def basename(entry: str) -> str:
    return entry.rstrip("/").split("/")[-1]


def parent_of(entry: str) -> str:
    parts = entry.rstrip("/").split("/")
    return "/".join(parts[:-1]) + "/" if len(parts) > 1 else ""


def ancestors(entry: str) -> List[str]:
    parts = entry.rstrip("/").split("/")
    return ["/".join(parts[:i]) + "/" for i in range(1, len(parts))]


def normalize_entries(entries: Iterable[str]) -> List[str]:
    """Strip './' and leading '/', add missing ancestor directories, dedupe, sort."""
    cleaned = set()
    for raw in entries:
        entry = raw.strip().replace("\\", "/")
        if not entry or entry.startswith("#"):
            continue
        while entry.startswith("./"):
            entry = entry[2:]
        entry = entry.lstrip("/")
        if entry in ("", "."):
            continue
        cleaned.add(entry)
    with_ancestors = set(cleaned)
    for entry in cleaned:
        with_ancestors.update(ancestors(entry))
    return sorted(with_ancestors)


def root_from_directory(data_location: str, root_storage_path: str, directory) -> Root:
    """List a real directory tree. Hidden entries are included; the config's excludePatterns decide."""
    base = pathlib.Path(directory)
    if not base.is_dir():
        raise ListingError(f"{directory} is not a directory")
    entries = []
    for current, dirnames, filenames in os.walk(base):
        rel = pathlib.Path(current).relative_to(base).as_posix()
        prefix = "" if rel == "." else rel + "/"
        entries.extend(prefix + d + "/" for d in dirnames)
        entries.extend(prefix + f for f in filenames)
    return Root(data_location, root_storage_path, normalize_entries(entries))


def root_from_lines(data_location: str, root_storage_path: str, lines: Iterable[str]) -> Root:
    """Build a root from `find`-style output: one path per line. A path that ends with '/' or
    has entries below it is a directory; everything else is a file."""
    raw = normalize_entries(lines)
    dirs = {parent for entry in raw for parent in ancestors(entry)}
    entries = set()
    for entry in raw:
        if is_dir(entry) or entry + "/" in dirs:
            entries.add(entry.rstrip("/") + "/")
        else:
            entries.add(entry)
    return Root(data_location, root_storage_path, sorted(entries))


def listing_from_dict(doc: dict) -> Listing:
    errors = list(jsonschema.Draft7Validator(load_schema(LISTING_SCHEMA)).iter_errors(doc))
    if errors:
        raise ListingError("\n".join(f"[{e.json_path}] {e.message}" for e in errors))
    roots = [Root(r["dataLocationIdentifier"], r["rootStoragePathIdentifier"], normalize_entries(r["entries"]))
             for r in doc["roots"]]
    return Listing(roots, doc.get("environmentIdentifier"))


def load_listing(path) -> Listing:
    with open(path, encoding="utf-8") as f:
        return listing_from_dict(json.load(f))


class Tree:
    """Children lookup over a root's entries."""

    def __init__(self, entries: Iterable[str]):
        self.entries = set(entries)
        self._children: Dict[str, List[str]] = defaultdict(list)
        for entry in sorted(self.entries):
            self._children[parent_of(entry)].append(entry)

    def children(self, directory: str) -> List[str]:
        return self._children.get(directory, [])
