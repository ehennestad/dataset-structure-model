"""The eval grader must accept good configs and reject bad ones.

`eval/grade.py` grades a config *writer* (the inference skill). It is only worth
anything if it fails the things a writer actually gets wrong, so every check it makes
has a test here that breaks a reference config and asserts the check fires.
"""
import copy
import importlib.util
import json
import pathlib
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).parent.parent
EVAL_CASES = REPO_ROOT / "eval" / "cases"

_spec = importlib.util.spec_from_file_location("dsm_eval_grade", REPO_ROOT / "eval" / "grade.py")
grade_module = importlib.util.module_from_spec(_spec)
sys.modules["dsm_eval_grade"] = grade_module
_spec.loader.exec_module(grade_module)


def case_names():
    return sorted(p.name for p in EVAL_CASES.iterdir() if p.is_dir())


def load(path):
    return json.loads(pathlib.Path(path).read_text())


def reference_config(case: str) -> dict:
    return load(REPO_ROOT / load(EVAL_CASES / case / "rubric.json")["referenceConfig"])


def grade_doc(case: str, doc: dict, tmp_path) -> dict:
    """Grade an in-memory config; returns {check name: Check}."""
    path = tmp_path / "candidate.json"
    path.write_text(json.dumps(doc))
    return {c.name: c for c in grade_module.grade(EVAL_CASES / case, path)}


def failures(checks: dict, include_skill_rules: bool = False) -> list:
    return sorted(name for name, c in checks.items()
                  if not c.ok and (include_skill_rules or not c.skill_only))


# --- the rubrics themselves are achievable ----------------------------------------

@pytest.mark.parametrize("case", case_names())
def test_rubric_is_satisfied_by_its_reference_config(case):
    """A rubric nobody has satisfied might be impossible. Each one has a config that does."""
    rubric = load(EVAL_CASES / case / "rubric.json")
    checks = grade_module.grade(EVAL_CASES / case, REPO_ROOT / rubric["referenceConfig"])
    assert not failures({c.name: c for c in checks}), f"{case}: reference config fails its own rubric"


@pytest.mark.parametrize("case", case_names())
def test_case_has_a_readme_and_a_listing(case):
    assert (EVAL_CASES / case / "README.md").read_text().strip()
    assert load(EVAL_CASES / case / "listing.json")["roots"]


# --- the grader rejects what a writer gets wrong -----------------------------------

def test_substring_collision_is_caught(tmp_path):
    """The m1001_s1 / m1001_s10 confusion: relax the anchor and two sessions merge."""
    doc = reference_config("flat-session-files")
    source = doc["dataLocations"][0]["filesystemSource"]
    # Drop the '_' that separates the running number from the rest of the file name.
    source["entityLayout"][0]["matchPattern"] = "^m\\d{3}-\\d{8}-\\d{3}.*$"
    for entry in source["metadataMapping"]:
        if entry["metadataRef"] == "session_id":
            entry["extraction"]["pattern"] = "^(m\\d{3}-\\d{8}-\\d{3})"

    checks = grade_doc("flat-session-files", doc, tmp_path)
    assert "distinct entities kept distinct" in failures(checks)
    assert "m110-20250510-0010_raw.tif" in checks["distinct entities kept distinct"].detail


def test_cross_location_identity_mismatch_is_caught(tmp_path):
    """Extract a different identity in `processed` and the shared session splits in two."""
    doc = reference_config("raw-processed-matching")
    processed = next(loc for loc in doc["dataLocations"] if loc["identifier"] == "processed")
    for entry in processed["filesystemSource"]["metadataMapping"]:
        if entry["metadataRef"] == "session_id":
            entry["extraction"]["pattern"] = "^session-m\\d{3}-\\d{8}-(\\d{3})$"

    checks = grade_doc("raw-processed-matching", doc, tmp_path)
    assert "identity reconciled across locations" in failures(checks)


def test_missing_exclude_patterns_is_caught(tmp_path):
    """Noise left unexplained shows up as no-match and blows the coverage budget."""
    doc = reference_config("folder-hierarchy-basic")
    doc["dataLocations"][0]["filesystemSource"]["entityLayout"][0]["excludePatterns"] = []

    checks = grade_doc("folder-hierarchy-basic", doc, tmp_path)
    assert "unexplained entries" in failures(checks)


def test_wrong_entity_count_is_caught(tmp_path):
    """A subject pattern that misses m220 leaves one subject where the listing has two."""
    doc = reference_config("folder-hierarchy-basic")
    doc["dataLocations"][0]["filesystemSource"]["entityLayout"][0]["matchPattern"] = "^m110$"

    checks = grade_doc("folder-hierarchy-basic", doc, tmp_path)
    assert "entity counts" in failures(checks)


def test_structural_subject_level_is_caught(tmp_path):
    """Making the subject level structural loses where the subject's data lives.

    The hierarchy survives: the walker infers the subject ancestor from the still-extracted
    `subject_id`, as `docs/guides/conformance.md` specifies. What is lost is the folder -
    the inferred records carry `locations: []` - so this is the check that fires.
    """
    doc = reference_config("folder-hierarchy-basic")
    del doc["dataLocations"][0]["filesystemSource"]["entityLayout"][0]["entityType"]

    checks = grade_doc("folder-hierarchy-basic", doc, tmp_path)
    assert "entities with their own folder or files (subject)" in failures(checks)
    assert "parent hierarchy" not in failures(checks)


def test_modelling_only_sessions_is_caught(tmp_path):
    """The realistic omission: model the sessions, ignore the subject their names imply.

    Every trace of `subject` has to go for this to validate, which is itself the point -
    the schema will not let a half-removed entity through.
    """
    doc = reference_config("flat-session-files")
    source = doc["dataLocations"][0]["filesystemSource"]
    source["metadataMapping"] = [e for e in source["metadataMapping"]
                                 if e["metadataRef"] != "subject_id"]
    doc["entityTypes"] = [e for e in doc["entityTypes"] if e["name"] != "subject"]
    doc["metadataDefinitions"].pop("subject_id", None)
    doc.pop("entityRelationships", None)

    checks = grade_doc("flat-session-files", doc, tmp_path)
    # Slots are positional, so one entity type where two were expected fails there first
    # and nothing further is comparable. That is the right signal: the omission is the
    # defect, not whatever the surviving records happen to look like.
    assert "entity types" in failures(checks)
    assert "1 (session)" in checks["entity types"].detail


def test_unextracted_dates_are_caught(tmp_path):
    """Drop the date rule and the required metadata values are no longer produced."""
    doc = reference_config("folder-hierarchy-basic")
    source = doc["dataLocations"][0]["filesystemSource"]
    source["metadataMapping"] = [e for e in source["metadataMapping"]
                                 if e["metadataRef"] != "session_date"]

    checks = grade_doc("folder-hierarchy-basic", doc, tmp_path)
    assert "metadata values (session)" in failures(checks)


def test_invalid_config_fails_the_gate_and_stops(tmp_path):
    """Validation is binary: nothing else is graded once it fails."""
    doc = reference_config("folder-hierarchy-basic")
    doc["dataLocations"][0]["filesystemSource"]["entityLayout"][0]["entityType"] = "nonexistent"

    checks = grade_doc("folder-hierarchy-basic", doc, tmp_path)
    assert list(checks) == ["validates"]
    assert not checks["validates"].ok


def test_function_extractor_is_flagged_as_a_skill_rule(tmp_path):
    """The conformance config for this case uses a function; the skill may not."""
    doc = load(REPO_ROOT / "conformance" / "function-extractor" / "config.json")
    checks = grade_doc("function-extractor", doc, tmp_path)
    assert checks["no function extractors"].skill_only
    assert "no function extractors" in failures(checks, include_skill_rules=True)
    # Independently of the skill rule, an unregistered function shows up in the walk.
    assert "no forbidden issue codes" in failures(checks)


def test_path_template_is_flagged_as_a_skill_rule(tmp_path):
    doc = reference_config("function-extractor")
    doc["dataLocations"][0]["filesystemSource"]["pathTemplate"] = "{rootPath}/{subject_id}"
    checks = grade_doc("function-extractor", doc, tmp_path)
    assert "no pathTemplate" in failures(checks, include_skill_rules=True)
    assert "no pathTemplate" not in failures(checks)


def test_entity_count_accepts_a_declared_range(tmp_path):
    """`[3, 4]` sessions: both the colliding and the separating reading pass."""
    doc = reference_config("folder-hierarchy-basic")
    layout = doc["dataLocations"][0]["filesystemSource"]["entityLayout"]
    # Make `_copy` its own session rather than a duplicate: 4 sessions instead of 3.
    layout[1]["matchPattern"] = "^\\d{8}_[a-z][a-z0-9_]*$"
    for entry in doc["dataLocations"][0]["filesystemSource"]["metadataMapping"]:
        if entry["metadataRef"] == "session_id":
            entry["extraction"] = {"method": "substring", "pattern": ":",
                                   "entityLayoutLevel": "sessions"}

    checks = grade_doc("folder-hierarchy-basic", doc, tmp_path)
    assert not failures(checks), failures(checks)


# --- the grader must be blind to naming -------------------------------------------

def rename_entity_types(doc: dict, mapping: dict) -> dict:
    """Rename entity types throughout. No literal folder text is involved."""
    doc = copy.deepcopy(doc)
    for entity in doc.get("entityTypes", []):
        entity["name"] = mapping.get(entity["name"], entity["name"])
    for definition in doc.get("metadataDefinitions", {}).values():
        definition["ofEntity"] = mapping.get(definition["ofEntity"], definition["ofEntity"])
    for relation in doc.get("entityRelationships", []):
        for key in ("sourceEntity", "targetEntity"):
            relation[key] = mapping.get(relation[key], relation[key])
    for location in doc.get("dataLocations", []):
        for level in (location.get("filesystemSource") or {}).get("entityLayout", []):
            if "entityType" in level:
                level["entityType"] = mapping.get(level["entityType"], level["entityType"])
    return doc


def rename_metadata_key(doc: dict, old: str, new: str) -> dict:
    """Rename a metadata definition, including `{token}` uses but not literal path text."""
    doc = copy.deepcopy(doc)
    definitions = doc["metadataDefinitions"]
    definitions[new] = definitions.pop(old)
    definitions[new]["name"] = new
    for entity in doc.get("entityTypes", []):
        if entity.get("identifierRef") == old:
            entity["identifierRef"] = new
    for location in doc.get("dataLocations", []):
        source = location.get("filesystemSource") or {}
        for entry in source.get("metadataMapping", []):
            if entry["metadataRef"] == old:
                entry["metadataRef"] = new
        for level in source.get("entityLayout", []):
            if "pathComponentTemplate" in level:
                level["pathComponentTemplate"] = level["pathComponentTemplate"].replace(
                    "{" + old + "}", "{" + new + "}")
            for pattern in level.get("filePatterns", []):
                pattern["pattern"] = pattern["pattern"].replace(
                    "{" + old + "}", "{" + new + "}")
    return doc


@pytest.mark.parametrize("case", case_names())
def test_renaming_entity_types_does_not_change_the_grade(case, tmp_path):
    """A listing cannot say `m110` is a "subject"; the skill asks the user. So the rubric
    treats its labels as slots resolved positionally, and animal/recording grades the same."""
    doc = rename_entity_types(reference_config(case),
                              {"subject": "animal", "session": "recording"})
    assert not failures(grade_doc(case, doc, tmp_path))


@pytest.mark.parametrize("case", case_names())
def test_renaming_metadata_fields_does_not_change_the_grade(case, tmp_path):
    """Nothing is graded on a metadata key - only on the values extracted."""
    doc = reference_config(case)
    if "session_id" not in doc.get("metadataDefinitions", {}):
        pytest.skip("case has no session_id to rename")
    doc = rename_metadata_key(doc, "session_id", "recording_key")
    assert not failures(grade_doc(case, doc, tmp_path))


def test_a_wrong_number_of_entity_types_is_caught(tmp_path):
    """Slots are positional, so the count has to match before anything is comparable."""
    doc = reference_config("folder-hierarchy-basic")
    doc["entityTypes"].append({"name": "trial", "identifierRef": "trial_id"})
    doc["metadataDefinitions"]["trial_id"] = {
        "name": "trial_id", "dataType": "string", "ofEntity": "trial"}

    checks = grade_doc("folder-hierarchy-basic", doc, tmp_path)
    assert "entity types" in failures(checks)


def test_identifier_mismatch_is_reported_not_crashed(tmp_path):
    """The config must use the identifiers the listing was built with.

    Left unchecked this raises a bare KeyError out of the walker, which is a crash rather
    than a diagnostic - see the note in the work item.
    """
    doc = reference_config("folder-hierarchy-basic")
    doc["dataLocations"][0]["identifier"] = "acquisition"

    checks = grade_doc("folder-hierarchy-basic", doc, tmp_path)
    assert "listing identifiers resolve" in failures(checks)
    assert "acquisition" in checks["listing identifiers resolve"].detail
