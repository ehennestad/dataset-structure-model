"""
Verify that every JSON file in examples/ validates against the schema.
Also verifies that a deliberately invalid instance is correctly rejected.
"""
import json

import jsonschema
import pytest

from conftest import EXAMPLES_DIR


def _load(path):
    with path.open() as f:
        return json.load(f)


def pytest_generate_tests(metafunc):
    if "example_path" in metafunc.fixturenames:
        paths = sorted(EXAMPLES_DIR.glob("*.json"))
        metafunc.parametrize("example_path", paths, ids=[p.name for p in paths])


def test_example_validates(example_path, schema):
    """Each example file must validate cleanly against the schema."""
    instance = _load(example_path)
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(instance))
    assert errors == [], (
        f"{example_path.name} has {len(errors)} validation error(s):\n"
        + "\n".join(f"  [{e.json_path}] {e.message}" for e in errors)
    )


def test_invalid_instance_is_rejected(schema):
    """An instance missing the required 'dataLocations' key must fail validation."""
    invalid = {
        "schemaVersion": "1.0.0",
        # deliberately omitting 'dataLocations'
    }
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(invalid))
    assert errors, "Expected validation errors for an instance missing 'dataLocations'"


def test_wrong_data_category_is_rejected(schema):
    """An instance with an invalid dataCategory enum value must fail validation."""
    bad_category = {
        "schemaVersion": "1.0.0",
        "dataLocations": [
            {
                "identifier": "test",
                "displayName": "Test",
                "dataCategory": "not-a-real-category",
                "rootStoragePaths": [
                    {"identifier": "p", "path": "/tmp", "storageType": "local"}
                ],
                "entityLayout": [
                    {"name": "subjects", "entityType": "subject", "matchPattern": ".*", "isVariable": True}
                ],
                "metadataMapping": [],
            }
        ],
    }
    validator = jsonschema.Draft7Validator(schema)
    errors = list(validator.iter_errors(bad_category))
    assert errors, "Expected validation errors for invalid dataCategory value"
