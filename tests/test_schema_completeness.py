"""
Structural checks on the schema:
- All $ref targets exist within the schema's $defs / definitions
- All definitions are referenced at least once (no dead code)
"""
import json
import re

import pytest

from conftest import SCHEMA_PATH


def _collect_refs(obj):
    """Recursively collect all $ref strings in a JSON object."""
    refs = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str):
                refs.add(v)
            else:
                refs |= _collect_refs(v)
    elif isinstance(obj, list):
        for item in obj:
            refs |= _collect_refs(item)
    return refs


def _definition_names(schema):
    """Return the set of definition names declared in definitions/$defs."""
    names = set()
    for key in ("definitions", "$defs"):
        names |= set(schema.get(key, {}).keys())
    return names


def test_all_refs_resolve(schema):
    """Every $ref in the schema points to a definition that exists."""
    refs = _collect_refs(schema)
    defined = _definition_names(schema)

    unresolved = []
    for ref in refs:
        # Only check local refs (#/definitions/... or #/$defs/...)
        if not ref.startswith("#/"):
            continue
        # Extract definition name from the ref path
        parts = ref.lstrip("#/").split("/")
        if parts[0] in ("definitions", "$defs") and len(parts) == 2:
            if parts[1] not in defined:
                unresolved.append(ref)

    assert unresolved == [], "Unresolved $refs: " + ", ".join(sorted(unresolved))


def test_no_unused_definitions(schema):
    """Every definition declared in the schema is referenced at least once."""
    defined = _definition_names(schema)
    refs = _collect_refs(schema)

    referenced_names = set()
    for ref in refs:
        if not ref.startswith("#/"):
            continue
        parts = ref.lstrip("#/").split("/")
        if parts[0] in ("definitions", "$defs") and len(parts) == 2:
            referenced_names.add(parts[1])

    unused = defined - referenced_names
    assert unused == set(), "Unused definitions (consider removing): " + ", ".join(sorted(unused))
