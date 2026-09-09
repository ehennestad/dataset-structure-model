"""
Cross-reference rules JSON Schema cannot express. Every example must satisfy
them; readers are expected to enforce the same rules.
"""
import re

import pytest

from conftest import EXAMPLES_DIR, load_json

TOKEN = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def check_references(doc):
    """Return a list of human-readable problems; empty when the doc is coherent."""
    problems = []
    entity_types = {e["name"] for e in doc.get("entityTypes", [])}
    definitions = doc.get("metadataDefinitions", {})
    locations = doc.get("dataLocations", [])
    location_ids = [loc["identifier"] for loc in locations]

    if len(set(e["name"] for e in doc.get("entityTypes", []))) != len(doc.get("entityTypes", [])):
        problems.append("entityTypes names are not unique")
    if len(set(location_ids)) != len(location_ids):
        problems.append("dataLocations identifiers are not unique")
    uuids = [loc["uuid"] for loc in locations if "uuid" in loc]
    if len(set(uuids)) != len(uuids):
        problems.append("dataLocations uuids are not unique")

    for et in doc.get("entityTypes", []):
        refs = [et["identifierRef"]] if "identifierRef" in et else et.get("identifierRefs", [])
        for ref in refs:
            if ref not in definitions:
                problems.append(f"entityType '{et['name']}' identity field '{ref}' is not in metadataDefinitions")
            elif definitions[ref]["ofEntity"] != et["name"]:
                problems.append(f"entityType '{et['name']}' identity field '{ref}' belongs to '{definitions[ref]['ofEntity']}'")

    for key, definition in definitions.items():
        if definition["ofEntity"] not in entity_types:
            problems.append(f"metadataDefinitions['{key}'].ofEntity '{definition['ofEntity']}' is not an entity type")

    for rel in doc.get("entityRelationships", []):
        for side in ("sourceEntity", "targetEntity"):
            if rel[side] not in entity_types:
                problems.append(f"entityRelationship {side} '{rel[side]}' is not an entity type")

    for loc in locations:
        for src in loc.get("derivedFrom", []):
            if src not in location_ids:
                problems.append(f"dataLocation '{loc['identifier']}' derivedFrom '{src}' is not a data location")
        source = loc.get("filesystemSource")
        if source is None:
            continue
        problems += _check_filesystem_source(loc["identifier"], source, entity_types, definitions)

    prefs = doc.get("preferences", {})
    default_loc = prefs.get("defaultDataLocationIdentifier")
    if default_loc is not None and default_loc not in location_ids:
        problems.append(f"preferences.defaultDataLocationIdentifier '{default_loc}' is not a data location")
    env = prefs.get("environmentIdentifier")
    if env is not None:
        envs = {
            rp.get("environment")
            for loc in locations
            for rp in loc.get("filesystemSource", {}).get("rootStoragePaths", [])
        }
        if env not in envs:
            problems.append(f"preferences.environmentIdentifier '{env}' matches no rootStoragePath.environment")
    return problems


def _check_filesystem_source(loc_id, source, entity_types, definitions):
    problems = []
    layout = source["entityLayout"]
    level_names = [level["name"] for level in layout]
    if len(set(level_names)) != len(level_names):
        problems.append(f"{loc_id}: entityLayout level names are not unique")
    for i, level in enumerate(layout):
        et = level.get("entityType")
        if et is not None and et not in entity_types:
            problems.append(f"{loc_id}: level '{level['name']}' entityType '{et}' is not an entity type")
        if level.get("fileSystemType") == "file" and i != len(layout) - 1:
            problems.append(f"{loc_id}: file level '{level['name']}' must be the last level")
        for token in TOKEN.findall(level.get("pathComponentTemplate", "")):
            if token not in definitions:
                problems.append(f"{loc_id}: level '{level['name']}' template token '{token}' is not a metadata field")
        pattern_names = [fp["name"] for fp in level.get("filePatterns", []) if "name" in fp]
        if len(set(pattern_names)) != len(pattern_names):
            problems.append(f"{loc_id}: level '{level['name']}' filePatterns names are not unique")
        for fp in level.get("filePatterns", []):
            for token in TOKEN.findall(fp["pattern"]):
                if token not in definitions:
                    problems.append(f"{loc_id}: filePattern '{fp['pattern']}' token '{token}' is not a metadata field")

    root_ids = [rp["identifier"] for rp in source["rootStoragePaths"]]
    if len(set(root_ids)) != len(root_ids):
        problems.append(f"{loc_id}: rootStoragePaths identifiers are not unique")

    for item in source.get("metadataMapping", []):
        ref = item["metadataRef"]
        if ref not in definitions:
            problems.append(f"{loc_id}: metadataMapping ref '{ref}' is not a metadata field")
        extraction = item["extraction"]
        level_ref = extraction.get("entityLayoutLevel")
        if isinstance(level_ref, str) and level_ref not in level_names:
            problems.append(f"{loc_id}: extraction for '{ref}' references unknown level '{level_ref}'")
        if isinstance(level_ref, int) and not 0 <= level_ref < len(layout):
            problems.append(f"{loc_id}: extraction for '{ref}' level index {level_ref} is out of range")
        if extraction["method"] == "template":
            for token in TOKEN.findall(extraction["pattern"]):
                if token not in definitions:
                    problems.append(f"{loc_id}: template for '{ref}' token '{token}' is not a metadata field")
                if token == ref:
                    problems.append(f"{loc_id}: template for '{ref}' references itself")
    return problems


def pytest_generate_tests(metafunc):
    if "example_path" in metafunc.fixturenames:
        paths = sorted(EXAMPLES_DIR.glob("*.json"))
        metafunc.parametrize("example_path", paths, ids=[p.name for p in paths])


def test_example_references_are_coherent(example_path):
    problems = check_references(load_json(example_path))
    assert problems == [], f"{example_path.name}:\n  " + "\n  ".join(problems)


def test_checker_detects_dangling_references():
    from conftest import minimal_config

    doc = minimal_config()
    doc["entityTypes"][0]["identifierRef"] = "missing"
    doc["dataLocations"][0]["filesystemSource"]["metadataMapping"][1]["extraction"]["entityLayoutLevel"] = "nope"
    doc["dataLocations"][0]["derivedFrom"] = ["ghost"]
    problems = check_references(doc)
    assert any("identity field 'missing'" in p for p in problems)
    assert any("unknown level 'nope'" in p for p in problems)
    assert any("derivedFrom 'ghost'" in p for p in problems)
