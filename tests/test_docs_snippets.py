"""
Every complete JSON document embedded in the docs validates against the
schema, so the documentation cannot drift from the schema unnoticed.
Fenced ```json blocks that are not complete documents (fragments with
"...", or objects without schemaVersion) are skipped.
"""
import json
import re

import jsonschema
import pytest

from conftest import DOCS_DIR, load_json
from test_reference_integrity import check_references

FENCE = re.compile(r"```json\n(.*?)```", re.DOTALL)


def _snippets():
    for md in sorted(DOCS_DIR.rglob("*.md")):
        if "_work-items" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        for i, block in enumerate(FENCE.findall(text)):
            try:
                doc = json.loads(block)
            except json.JSONDecodeError:
                continue
            if isinstance(doc, dict) and "schemaVersion" in doc:
                yield pytest.param((md, doc), id=f"{md.relative_to(DOCS_DIR)}#{i}")


def pytest_generate_tests(metafunc):
    if "snippet" in metafunc.fixturenames:
        metafunc.parametrize("snippet", list(_snippets()))


def test_docs_snippet_validates(snippet, schema):
    md, doc = snippet
    errors = list(jsonschema.Draft7Validator(schema).iter_errors(doc))
    assert errors == [], f"{md}:\n" + "\n".join(f"  [{e.json_path}] {e.message}" for e in errors)
    problems = check_references(doc)
    assert problems == [], f"{md}:\n  " + "\n  ".join(problems)


def test_docs_have_at_least_one_complete_snippet():
    assert list(_snippets()), "expected complete JSON examples in the docs"
