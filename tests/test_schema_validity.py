"""
Verify that the schema file itself is valid JSON and conforms to the
JSON Schema draft-07 meta-schema.
"""
import json

import jsonschema
import pytest

from conftest import SCHEMA_PATH


def test_schema_is_valid_json():
    """Schema file parses as valid JSON without error."""
    with SCHEMA_PATH.open() as f:
        data = json.load(f)
    assert isinstance(data, dict)


def test_schema_declares_draft07(schema):
    assert schema.get("$schema") == "http://json-schema.org/draft-07/schema#"


def test_schema_validates_against_draft07_meta_schema(schema):
    """Schema is valid according to the draft-07 meta-schema."""
    meta = jsonschema.Draft7Validator.META_SCHEMA
    validator = jsonschema.Draft7Validator(meta)
    errors = list(validator.iter_errors(schema))
    assert errors == [], "\n".join(str(e) for e in errors)


def test_schema_has_required_top_level_keys(schema):
    for key in ("$schema", "title", "type", "properties"):
        assert key in schema, f"Missing top-level key: {key!r}"


def test_schema_requires_schema_version(schema):
    required = schema.get("required", [])
    assert "schemaVersion" in required
