"""
The EntityRecord and DirectoryListing schemas are valid draft-07, and every
record in the conformance expectations validates.
"""
import jsonschema
import pytest

from conftest import CONFORMANCE_DIR, load_json


def _meta_errors(schema):
    meta = jsonschema.Draft7Validator.META_SCHEMA
    return list(jsonschema.Draft7Validator(meta).iter_errors(schema))


def test_entity_record_schema_is_valid_draft07(entity_record_schema):
    assert _meta_errors(entity_record_schema) == []


def test_directory_listing_schema_is_valid_draft07(directory_listing_schema):
    assert _meta_errors(directory_listing_schema) == []


def pytest_generate_tests(metafunc):
    if "expected_path" in metafunc.fixturenames:
        paths = sorted(CONFORMANCE_DIR.glob("*/expected.json"))
        metafunc.parametrize("expected_path", paths, ids=[p.parent.name for p in paths])


def test_expected_records_validate(expected_path, entity_record_schema):
    expected = load_json(expected_path)
    validator = jsonschema.Draft7Validator(entity_record_schema)
    for i, record in enumerate(expected.get("records", [])):
        errors = list(validator.iter_errors(record))
        assert errors == [], (
            f"{expected_path.parent.name} record {i} has {len(errors)} validation error(s):\n"
            + "\n".join(f"  [{e.json_path}] {e.message}" for e in errors)
        )


def test_record_shape_rules(entity_record_schema):
    validator = jsonschema.Draft7Validator(entity_record_schema)
    assert list(validator.iter_errors({"entityType": "session", "identity": {}, "locations": []}))
    inferred_ancestor = {"entityType": "subject", "identity": {"subject_id": "m110"}, "locations": []}
    assert list(validator.iter_errors(inferred_ancestor)) == []
    with_issue = dict(inferred_ancestor, issues=[{"code": "extraction-failed", "message": "x"}])
    assert list(validator.iter_errors(with_issue)) == []
    bad_issue = dict(inferred_ancestor, issues=["free text is not enough"])
    assert list(validator.iter_errors(bad_issue))
    unknown_code = dict(inferred_ancestor, issues=[{"code": "made-up"}])
    assert list(validator.iter_errors(unknown_code))
