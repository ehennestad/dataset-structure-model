"""The dsm-infer-config skill: its bundled script, and its own integrity.

The skill's prose is not tested. Its script, its frontmatter, the files it tells the
agent to read, and the shell commands it prints are, because a skill that points at a
missing file or prints a command that errors is worse than no skill.
"""
import importlib.util
import pathlib
import re
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).parent.parent
SKILL_DIR = REPO_ROOT / "skills" / "dsm-infer-config"
SKILL_MD = SKILL_DIR / "SKILL.md"

_spec = importlib.util.spec_from_file_location("dsm_survey", SKILL_DIR / "scripts" / "survey.py")
survey_module = importlib.util.module_from_spec(_spec)
sys.modules["dsm_survey"] = survey_module
_spec.loader.exec_module(survey_module)


# --- the survey script -------------------------------------------------------------

@pytest.mark.parametrize("name,expected", [
    ("m110", "A1#3"),
    ("2025_05_23", "#4_#2_#2"),
    ("sub-AB01", "A3-A2#2"),
    ("rec.raw", "A3.A3"),
    ("m110-20250510-001_raw.tif", "A1#3-#8-#3_A3.A3"),
])
def test_shape_keeps_run_lengths(name, expected):
    assert survey_module.shape(name) == expected


def test_loose_shape_drops_run_lengths():
    assert survey_module.shape("m110-20250510-001", widths=False) == "A#-#-#"


def test_shape_separates_the_collision_trap():
    """`-001` and `-0010` must be two shapes, or the survey hides the trap."""
    assert (survey_module.shape("m110-20250510-001_raw.tif")
            != survey_module.shape("m110-20250510-0010_raw.tif"))


def test_loose_shape_hides_the_trap():
    """Which is why run lengths are the default, not an option."""
    assert (survey_module.shape("m110-20250510-001_raw.tif", widths=False)
            == survey_module.shape("m110-20250510-0010_raw.tif", widths=False))


@pytest.mark.parametrize("name,expected", [
    ("2019_07_09_0000_IV(-70mV).abf", ".abf"),
    ("08-07-2019 C4_shrinkcorr_3.06.rar", ".rar"),
    ("archive.tar.gz", ".tar.gz"),
    ("README", "(none)"),
])
def test_extension_ignores_numbers_in_the_stem(name, expected):
    """A version or scale number before the suffix must not split the histogram."""
    assert survey_module.extension(name) == expected


@pytest.mark.parametrize("case", sorted(p.name for p in (REPO_ROOT / "eval" / "cases").iterdir()
                                        if p.is_dir()))
def test_survey_runs_on_every_eval_listing(case):
    listing = REPO_ROOT / "eval" / "cases" / case / "listing.json"
    result = subprocess.run(
        [sys.executable, str(SKILL_DIR / "scripts" / "survey.py"), str(listing)],
        capture_output=True, text=True, check=True)
    assert result.stdout.strip()


def test_survey_reports_every_entry():
    """Aggregation must not drop anything: the per-depth counts sum to the entry count."""
    import json
    listing = json.loads((REPO_ROOT / "eval" / "cases"
                          / "raw-processed-matching" / "listing.json").read_text())
    text = survey_module.survey(listing)
    for root in listing["roots"]:
        counted = sum(int(folders) + int(files) for folders, files in
                      re.findall(r"depth \d+: (\d+) folder\(s\), (\d+) file\(s\)", text))
        assert counted >= len(root["entries"])


# --- the skill's own integrity -----------------------------------------------------

def test_frontmatter_has_name_and_description():
    head = SKILL_MD.read_text().split("---")[1]
    assert re.search(r"^name: dsm-infer-config$", head, re.M)
    description = re.search(r"^description: (.+)$", head, re.M)
    assert description and len(description.group(1)) > 120, "description drives triggering"


def test_every_referenced_file_exists():
    """`reference/*.md` are symlinks into docs/, so they cannot drift from the schema."""
    text = SKILL_MD.read_text()
    for relative in re.findall(r"`((?:reference|scripts)/[\w.-]+)`", text):
        target = SKILL_DIR / relative
        assert target.exists(), f"SKILL.md points at missing {relative}"
        if target.is_symlink():
            assert target.resolve().is_relative_to(REPO_ROOT / "docs")


def test_reference_docs_are_symlinks_not_copies():
    for reference in (SKILL_DIR / "reference").iterdir():
        assert reference.is_symlink(), f"{reference.name} is a copy and will drift"


def test_hard_rules_name_every_forbidden_construct():
    """AGENTS.md forbids these; the skill has to say so explicitly."""
    text = SKILL_MD.read_text()
    for forbidden in ["function", "sidecar", "pathTemplate", "preferences",
                      "spreadsheet", "database", "api"]:
        assert forbidden in text, f"the skill never mentions {forbidden}"


def test_skill_does_not_recommend_draft_source_types():
    """Mentioning them is required; presenting them as usable is not."""
    text = SKILL_MD.read_text()
    assert "Never emit DRAFT parts" in text
    assert '`"0:end"`' not in text or "Never" in text
