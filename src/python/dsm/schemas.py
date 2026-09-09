"""Locate the JSON schemas: packaged copies when installed, the repo's schema/ folder when run in place."""
import json
import pathlib

CONFIG_SCHEMA = "DatasetStructureModel.schema.json"
RECORD_SCHEMA = "EntityRecord.schema.json"
LISTING_SCHEMA = "DirectoryListing.schema.json"

_PACKAGE_DIR = pathlib.Path(__file__).parent
_CANDIDATE_DIRS = [_PACKAGE_DIR / "schemas", _PACKAGE_DIR.parent.parent.parent / "schema"]


def schema_path(name):
    for directory in _CANDIDATE_DIRS:
        candidate = directory / name
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"schema {name} not found in {[str(d) for d in _CANDIDATE_DIRS]}")


def load_schema(name):
    return json.loads(schema_path(name).read_text(encoding="utf-8"))
