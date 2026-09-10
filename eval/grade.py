"""Grade a candidate DSM config against an eval rubric.

The conformance fixtures check a *reader*: same config, same listing, same records.
This checks a *writer*: given only a listing, is the config it produced any good?

A listing does not determine a config uniquely, so grading on record equality would
fail reasonable output (see docs/_work-items/2026-09-10-config-inference-skill).
Every check here is therefore blind to how fields are named and to which extraction
method was chosen; what is graded is what the config *achieves* when walked.

    python eval/grade.py eval/cases/<case> <candidate>.json
    python eval/grade.py --reference            # rubrics vs. the reference configs
"""
import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src" / "python"))

from dsm.errors import ConfigError                     # noqa: E402
from dsm.extract import ExtractorRegistry              # noqa: E402
from dsm.listing import load_listing                   # noqa: E402
from dsm.validate import load_config                   # noqa: E402
from dsm.walk import walk                              # noqa: E402


class Check:
    """One graded criterion.

    `skill_only` marks a rule about what the *skill* may emit rather than about what a
    good config looks like. A hand-written config may legitimately carry `pathTemplate`;
    the skill may not, because a read-only listing cannot confirm a write convention.
    `--reference` reports these but does not fail on them.
    """

    def __init__(self, name: str, ok: bool, detail: str = "", skill_only: bool = False):
        self.name = name
        self.ok = ok
        self.detail = detail
        self.skill_only = skill_only

    def to_dict(self) -> dict:
        return {"check": self.name, "ok": self.ok, "detail": self.detail,
                "skillOnly": self.skill_only}


# --- static checks on the config document, before it is ever walked ----------------

def _extractions(doc: dict):
    for loc in doc.get("dataLocations", []):
        source = loc.get("filesystemSource") or {}
        for entry in source.get("metadataMapping", []):
            yield loc.get("identifier"), entry.get("extraction", {})


def _static_checks(doc: dict, rubric: dict) -> List[Check]:
    checks = []
    if rubric.get("forbidFunctionExtractors", True):
        used = [f"{loc}:{e.get('extractorFunction')}" for loc, e in _extractions(doc)
                if e.get("method") == "function"]
        checks.append(Check(
            "no function extractors",
            not used,
            detail="the skill must not emit `function`; it needs code in every reader"
            + (f" (found {', '.join(used)})" if used else ""),
            skill_only=True,
        ))
    if rubric.get("forbidPathTemplate", True):
        used = [loc.get("identifier") for loc in doc.get("dataLocations", [])
                if (loc.get("filesystemSource") or {}).get("pathTemplate")]
        checks.append(Check(
            "no pathTemplate",
            not used,
            detail="a read-only listing cannot confirm a write convention"
            + (f" (found on {', '.join(map(str, used))})" if used else ""),
            skill_only=True,
        ))
    return checks


# --- rubric checks over the walk result -------------------------------------------

def _parent_chain(record) -> List[str]:
    return [entity_type for entity_type, _ in record.parents]


def _stringify(value: Any) -> str:
    return json.dumps(value) if isinstance(value, (dict, list)) else str(value)


def _match_value_sets(records, required: List[List[str]]) -> Optional[str]:
    """Each required value set needs its own distinct record. Returns a failure note."""
    pools = []
    for wanted in required:
        candidates = {
            i for i, r in enumerate(records)
            if set(wanted) <= {_stringify(v) for v in r.metadata.values()}
        }
        if not candidates:
            return f"no {records[0].entity_type if records else 'record'} carries all of {wanted}"
        pools.append((wanted, candidates))

    used: Dict[int, int] = {}

    def assign(i: int) -> bool:
        if i == len(pools):
            return True
        for candidate in sorted(pools[i][1]):
            if candidate in used:
                continue
            used[candidate] = i
            if assign(i + 1):
                return True
            del used[candidate]
        return False

    if not assign(0):
        return "value sets do not map onto distinct records (one record claimed by two)"
    return None


def _entity_slots(config, rubric: dict):
    """Map the rubric's entity-type labels onto the candidate's own names, by position.

    A listing cannot tell you that `m110` is a "subject" rather than an "animal" or a
    "cage" - that is a semantic choice the skill puts to the user, so the eval must not
    require a particular word. Rubric labels are therefore *slots*, resolved against the
    candidate's `entityTypes` in declaration order (which the schema already pins to
    layout order). A config naming them animal/recording is graded exactly like one
    naming them subject/session.
    """
    labels = rubric.get("entityTypes")
    actual = config.entity_types
    if not labels:
        return {name: name for name in actual}, None
    if len(labels) != len(actual):
        return None, (f"expected {len(labels)} entity type(s) ({', '.join(labels)}), "
                      f"config declares {len(actual)} ({', '.join(actual) or 'none'})")
    return dict(zip(labels, actual)), None


def _rubric_checks(config, result, rubric: dict) -> List[Check]:
    checks = []
    records = result.records

    slots, problem = _entity_slots(config, rubric)
    if problem:
        return [Check("entity types", False, problem)]
    resolve = lambda label: slots.get(label, label)  # noqa: E731

    expected_counts = rubric.get("entityCounts")
    if expected_counts is not None:
        # A value may be an exact count or [min, max]: some listings genuinely admit
        # two defensible answers (whether a `_copy` folder is its own entity, say).
        actual = {label: sum(1 for r in records if r.entity_type == resolve(label))
                  for label in expected_counts}
        wrong = []
        for label, allowed in expected_counts.items():
            low, high = allowed if isinstance(allowed, list) else (allowed, allowed)
            if not low <= actual[label] <= high:
                span = f"{low}" if low == high else f"{low}-{high}"
                wrong.append(f"{resolve(label)}: {actual[label]} (want {span})")
        extra = sorted({r.entity_type for r in records}
                       - {resolve(label) for label in expected_counts})
        if extra:
            wrong.append("unexpected entity type(s): " + ", ".join(extra))
        checks.append(Check("entity counts", not wrong, "; ".join(wrong)))

    hierarchy = rubric.get("hierarchy")
    if hierarchy is not None:
        expected_chain = {resolve(label): [resolve(p) for p in chain]
                          for label, chain in hierarchy.items()}
        wrong = [
            f"{r.entity_type}{r.identity}: parents {_parent_chain(r)} "
            f"!= {expected_chain[r.entity_type]}"
            for r in records
            if r.entity_type in expected_chain and _parent_chain(r) != expected_chain[r.entity_type]
        ]
        checks.append(Check("parent hierarchy", not wrong, "; ".join(wrong[:3])))

    max_no_match = rubric.get("maxNoMatch")
    if max_no_match is not None:
        offenders = [u for u in result.unmatched if u.reason == "no-match"]
        checks.append(Check(
            "unexplained entries",
            len(offenders) <= max_no_match,
            f"{len(offenders)} no-match (allowed {max_no_match}): "
            + ", ".join(u.path for u in offenders[:4]),
        ))

    minimum = rubric.get("minMultiLocationEntities")
    if minimum is not None:
        matched = [r for r in records if len({loc.data_location for loc in r.locations}) >= 2]
        checks.append(Check(
            "identity reconciled across locations",
            len(matched) >= minimum,
            f"{len(matched)} entit(ies) resolve to one record spanning >1 location, need {minimum}",
        ))

    for label, minimum in (rubric.get("minEntitiesWithLocations") or {}).items():
        entity_type = resolve(label)
        # An entity whose level is structural still gets a record, because the walker
        # infers ancestors from a descendant's extracted id - but with `locations: []`,
        # so where its data lives is lost. This is what separates "modelled the folder"
        # from "let the entity be inferred".
        owning = [r for r in records if r.entity_type == entity_type and r.locations]
        checks.append(Check(
            f"entities with their own folder or files ({entity_type})",
            len(owning) >= minimum,
            f"{len(owning)} of {sum(1 for r in records if r.entity_type == entity_type)} "
            f"have a location, need {minimum}",
        ))

    forbidden = set(rubric.get("forbiddenIssueCodes", []))
    if forbidden:
        seen = sorted({i.code for r in records for i in r.issues} & forbidden)
        checks.append(Check("no forbidden issue codes", not seen, f"found {seen}" if seen else ""))

    for group in rubric.get("pathsMustNotShareRecord") or []:
        # The substring trap: a pattern matched by containment puts `..._0010_raw.tif`
        # and `..._001_raw.tif` under one identity. A token or anchored pattern does not.
        collisions = [
            f"{r.entity_type}{r.identity} holds " + ", ".join(sorted(set(group) & owned))
            for r in records
            for owned in [{p for loc in r.locations for p in loc.paths}]
            if len(set(group) & owned) > 1
        ]
        checks.append(Check(
            "distinct entities kept distinct",
            not collisions,
            "; ".join(collisions) or f"{' and '.join(group)} land in separate records",
        ))

    for label, required in (rubric.get("metadataValueSets") or {}).items():
        entity_type = resolve(label)
        subset = [r for r in records if r.entity_type == entity_type]
        note = _match_value_sets(subset, required)
        checks.append(Check(f"metadata values ({entity_type})", note is None, note or ""))

    return checks


# --- driver ------------------------------------------------------------------------

def grade(case_dir: pathlib.Path, config_path: pathlib.Path) -> List[Check]:
    rubric = json.loads((case_dir / "rubric.json").read_text())
    try:
        config = load_config(config_path, reject_draft=True)
    except ConfigError as e:
        return [Check("validates", False,
                      f"{e.code}: " + "; ".join(str(p) for p in e.problems[:3]))]

    checks = [Check("validates", True, "schema, cross-references and no DRAFT blocks")]
    checks += _static_checks(config.doc, rubric)

    listing = load_listing(case_dir / "listing.json")
    # The config has to use the identifiers the listing was built with, or the walk cannot
    # resolve its roots. Reported as a check rather than left to raise KeyError from walk().
    declared = {(loc["identifier"], rp["identifier"])
                for loc in config.doc.get("dataLocations", [])
                for rp in (loc.get("filesystemSource") or {}).get("rootStoragePaths", [])}
    needed = {(root.data_location, root.root_storage_path) for root in listing.roots}
    missing = sorted(needed - declared)
    checks.append(Check(
        "listing identifiers resolve",
        not missing,
        "the listing names " + ", ".join(f"{loc}/{root}" for loc, root in missing)
        + "; the config declares " + (", ".join(f"{loc}/{root}" for loc, root in sorted(declared)) or "none")
        if missing else "",
    ))
    if missing:
        return checks

    result = walk(config, listing, ExtractorRegistry())
    checks += _rubric_checks(config, result, rubric)
    return checks


def _report(case_name: str, checks: List[Check], verbose: bool,
            skip_skill_rules: bool = False) -> bool:
    graded = [c for c in checks if not (skip_skill_rules and c.skill_only)]
    passed = all(c.ok for c in graded)
    print(f"{'PASS' if passed else 'FAIL'}  {case_name}")
    for check in checks:
        advisory = skip_skill_rules and check.skill_only
        if check.ok and not verbose:
            continue
        mark = "ok  " if check.ok else ("note" if advisory else "FAIL")
        suffix = " (skill rule, not graded here)" if advisory and not check.ok else ""
        print(f"       {mark} {check.name}"
              + (f" - {check.detail}" if check.detail else "") + suffix)
    return passed


def main(argv=None) -> int:
    root = pathlib.Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Grade a DSM config against an eval rubric")
    parser.add_argument("case", nargs="?", help="eval/cases/<name>")
    parser.add_argument("config", nargs="?", help="the candidate config to grade")
    parser.add_argument("--reference", action="store_true",
                        help="grade each case's reference config (checks the rubrics themselves)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    if args.reference:
        failed = 0
        for case_dir in sorted(p for p in (root / "cases").iterdir() if p.is_dir()):
            meta = json.loads((case_dir / "rubric.json").read_text())
            reference = meta.get("referenceConfig")
            if not reference:
                print(f"SKIP  {case_dir.name} (no referenceConfig)")
                continue
            failed += not _report(case_dir.name, grade(case_dir, root.parent / reference),
                                  args.verbose, skip_skill_rules=True)
        print("all rubrics satisfied by their reference config" if not failed
              else f"{failed} rubric(s) not satisfied by their own reference config")
        return 1 if failed else 0

    if not args.case or not args.config:
        parser.error("give a case directory and a candidate config, or --reference")
    case_dir = pathlib.Path(args.case)
    return 0 if _report(case_dir.name, grade(case_dir, pathlib.Path(args.config)), args.verbose) else 1


if __name__ == "__main__":
    sys.exit(main())
