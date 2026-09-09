"""Command line: validate | listing | walk | compare | conformance."""
import argparse
import importlib
import importlib.util
import json
import pathlib
import sys
from typing import List, Optional

from . import __version__
from .compare import compare_results
from .conformance import FIXTURE_EXTRACTORS, run_cases
from .errors import ConfigError, ListingError
from .extract import ExtractorRegistry
from .listing import Listing, load_listing, root_from_directory, root_from_lines
from .report import render_report
from .validate import load_config
from .walk import walk


def _load_extractors(spec: Optional[str]) -> ExtractorRegistry:
    """A module (dotted name or .py path) exposing EXTRACTORS = {key: callable}."""
    registry = ExtractorRegistry()
    if not spec:
        return registry
    if spec.endswith(".py"):
        module_spec = importlib.util.spec_from_file_location("dsm_extractors", spec)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
    else:
        module = importlib.import_module(spec)
    for key, fn in getattr(module, "EXTRACTORS", {}).items():
        registry.register(key, fn)
    return registry


def _repo_conformance_dir() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent.parent.parent.parent / "conformance"


def cmd_validate(args) -> int:
    try:
        config = load_config(args.config, reject_draft=not args.allow_draft)
    except ConfigError as e:
        print(f"{args.config}: {e.code}")
        for problem in e.problems:
            print(f"  {problem}")
        return 1
    print(f"{args.config}: valid ({len(config.locations)} data location(s), {len(config.entity_types)} entity type(s))")
    return 0


def cmd_listing(args) -> int:
    if len(args.spec) % 3 != 0:
        print("listing takes triplets: LOCATION ROOT DIRECTORY [LOCATION ROOT DIRECTORY ...]", file=sys.stderr)
        return 2
    roots = []
    for i in range(0, len(args.spec), 3):
        loc_id, root_id, source = args.spec[i:i + 3]
        try:
            if args.text:
                with open(source, encoding="utf-8") as f:
                    roots.append(root_from_lines(loc_id, root_id, f.readlines()))
            else:
                roots.append(root_from_directory(loc_id, root_id, source))
        except ListingError as e:
            print(str(e), file=sys.stderr)
            return 1
    listing = Listing(roots, args.environment)
    text = listing.to_json()
    if args.output:
        pathlib.Path(args.output).write_text(text, encoding="utf-8")
        print(f"wrote {args.output} ({sum(len(r.entries) for r in roots)} entries)")
    else:
        sys.stdout.write(text)
    return 0


def cmd_walk(args) -> int:
    try:
        config = load_config(args.config, reject_draft=not args.allow_draft)
    except ConfigError as e:
        print(f"{args.config}: {e.code}", file=sys.stderr)
        for problem in e.problems:
            print(f"  {problem}", file=sys.stderr)
        return 1
    try:
        listing = load_listing(args.listing)
    except ListingError as e:
        print(f"{args.listing}: invalid listing\n{e}", file=sys.stderr)
        return 1
    if args.environment:
        listing.environment = args.environment
    result = walk(config, listing, _load_extractors(args.extractors))
    if args.json:
        json.dump(result.to_dict(), sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_report(config, result))
    if args.fail_on_issues and any(r.issues for r in result.records):
        return 3
    return 0


def cmd_compare(args) -> int:
    with open(args.expected, encoding="utf-8") as f:
        expected = json.load(f)
    with open(args.actual, encoding="utf-8") as f:
        actual = json.load(f)
    diffs = compare_results(expected, actual)
    if diffs:
        print(f"{len(diffs)} difference(s):")
        for d in diffs:
            print(f"  {d}")
        return 1
    print("equal")
    return 0


def cmd_conformance(args) -> int:
    directory = pathlib.Path(args.directory) if args.directory else _repo_conformance_dir()
    registry = ExtractorRegistry(FIXTURE_EXTRACTORS)
    if args.extractors:
        extra = _load_extractors(args.extractors)
        for key in extra.keys():
            registry.register(key, extra.get(key))
    results = run_cases(directory, registry)
    failed = 0
    for r in results:
        print(f"{r.status.upper():5} {r.name}")
        if r.status != "pass" and (args.verbose or r.status == "fail"):
            for d in r.diffs:
                print(f"      {d}")
        failed += r.status == "fail"
    passed = sum(r.status == "pass" for r in results)
    skipped = sum(r.status == "skip" for r in results)
    print(f"{passed} passed, {failed} failed, {skipped} skipped")
    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dsm", description="Dataset Structure Model reference reader")
    parser.add_argument("--version", action="version", version=f"dsm {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="validate a config (schema, cross-references, DRAFT blocks)")
    p.add_argument("config")
    p.add_argument("--allow-draft", action="store_true", help="accept DRAFT source types and sidecar rules")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("listing", help="build a listing.json from directories or find-style text files")
    p.add_argument("spec", nargs="+", metavar="LOCATION ROOT SOURCE")
    p.add_argument("--text", action="store_true", help="SOURCE files hold one relative path per line instead of being directories")
    p.add_argument("--environment")
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_listing)

    p = sub.add_parser("walk", help="walk a listing into entity records (dry run)")
    p.add_argument("config")
    p.add_argument("listing")
    p.add_argument("--json", action="store_true", help="print records and unmatched entries as JSON")
    p.add_argument("--environment")
    p.add_argument("--extractors", help="module (dotted or .py) exposing EXTRACTORS = {key: callable}")
    p.add_argument("--allow-draft", action="store_true")
    p.add_argument("--fail-on-issues", action="store_true", help="exit 3 when any record carries an issue")
    p.set_defaults(func=cmd_walk)

    p = sub.add_parser("compare", help="compare a reader's output with an expectation")
    p.add_argument("expected")
    p.add_argument("actual")
    p.set_defaults(func=cmd_compare)

    p = sub.add_parser("conformance", help="run the conformance cases against this reader")
    p.add_argument("directory", nargs="?", help="cases directory (default: the repository's conformance/)")
    p.add_argument("--extractors")
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(func=cmd_conformance)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
