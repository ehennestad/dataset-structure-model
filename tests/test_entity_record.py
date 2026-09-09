"""
The EntityRecord schema is valid draft-07 and every example record validates.
"""
import jsonschema
import pytest

from conftest import ENTITY_RECORD_SCHEMA_PATH, RECORDS_DIR, load_json


def test_entity_record_schema_is_valid_draft07(entity_record_schema):
    meta = jsonschema.Draft7Validator.META_SCHEMA
    errors = list(jsonschema.Draft7Validator(meta).iter_errors(entity_record_schema))
    assert errors == [], "\n".join(str(e) for e in errors)


def pytest_generate_tests(metafunc):
    if "records_path" in metafunc.fixturenames:
        paths = sorted(RECORDS_DIR.glob("*.json"))
        metafunc.parametrize("records_path", paths, ids=[p.name for p in paths])


def test_example_records_validate(records_path, entity_record_schema):
    records = load_json(records_path)
    assert isinstance(records, list) and records, "records file must hold a non-empty array"
    validator = jsonschema.Draft7Validator(entity_record_schema)
    for i, record in enumerate(records):
        errors = list(validator.iter_errors(record))
        assert errors == [], (
            f"{records_path.name}[{i}] has {len(errors)} validation error(s):\n"
            + "\n".join(f"  [{e.json_path}] {e.message}" for e in errors)
        )


def test_record_requires_identity_and_location(entity_record_schema):
    validator = jsonschema.Draft7Validator(entity_record_schema)
    assert list(validator.iter_errors({"entityType": "session", "identity": {}, "locations": []}))
    ok = {
        "entityType": "session",
        "identity": {"session_id": "s1"},
        "locations": [{"dataLocationIdentifier": "raw", "rootStoragePathIdentifier": "main", "paths": ["m1/s1"]}],
    }
    assert list(validator.iter_errors(ok)) == []
