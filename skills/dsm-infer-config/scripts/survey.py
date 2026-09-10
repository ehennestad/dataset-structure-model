"""Summarise a directory listing into the name families a config has to describe.

Pattern inference needs every *shape* a sibling name takes, not every name. This
aggregates, so it stays readable on a tree of any size: a 40k-session dataset whose
folders all look like `m110-20250523-001` prints one line.

    python survey.py listing.json                 # all locations
    python survey.py listing.json --depth 2       # one depth, with every distinct name
    python survey.py listing.json --max-examples 6

Shapes collapse runs of one character class and keep each run's length:
  m110 -> A1#3,   2025_05_23 -> #4_#2_#2,   sub-AB01 -> A3-A2#2,   rec.raw -> A3.A3
A shape shared by every sibling at a depth is a `matchPattern` waiting to be written.
Two shapes at one depth mean either a structural level beside an entity level, or noise
to exclude. A shape with a count of 1 next to a near-identical shape with a high count
is usually either the outlier that breaks a naive pattern, or a stray file.
Pass --loose to drop the lengths when you only want the name families.
"""
import argparse
import collections
import json
import pathlib
import re
import sys


def shape(name: str, widths: bool = True) -> str:
    r"""Collapse runs of digits to '#', runs of letters to 'A', keep separators.

    With `widths`, a run carries its length: `m110-20250510-001` -> `A1#3-#8-#3`. The
    length is the whole point - it is what tells you to write `\d{8}` rather than `\d+`,
    and it is what makes `-001` and `-0010` two shapes instead of one. The collapsed
    view (`--loose`) groups name families more aggressively and is easier to skim.
    """
    out = []
    for run in re.findall(r"\d+|[A-Za-z]+|[^0-9A-Za-z]", name):
        if not run[0].isalnum():
            out.append(run)
        else:
            symbol = "#" if run[0].isdigit() else "A"
            out.append(f"{symbol}{len(run)}" if widths else symbol)
    return "".join(out)


def survey(listing: dict, only_depth=None, max_examples=4, widths=True) -> str:
    lines = []
    for root in listing.get("roots", []):
        entries = root.get("entries", [])
        lines.append(f"{root['dataLocationIdentifier']}/{root['rootStoragePathIdentifier']}"
                     f"  ({len(entries)} entries)")
        by_depth = collections.defaultdict(list)
        for entry in entries:
            is_dir = entry.endswith("/")
            parts = entry.rstrip("/").split("/")
            by_depth[len(parts)].append((parts[-1], is_dir))

        for depth in sorted(by_depth):
            if only_depth is not None and depth != only_depth:
                continue
            names = by_depth[depth]
            folders = [n for n, d in names if d]
            files = [n for n, d in names if not d]
            lines.append(f"  depth {depth}: {len(folders)} folder(s), {len(files)} file(s)")

            for label, group in (("folder", folders), ("file", files)):
                if not group:
                    continue
                shapes = collections.Counter(shape(n, widths) for n in group)
                examples = collections.defaultdict(list)
                for name in group:
                    examples[shape(name, widths)].append(name)
                for shp, count in shapes.most_common():
                    sample = sorted(set(examples[shp]))
                    shown = sample if only_depth is not None else sample[:max_examples]
                    more = "" if len(shown) == len(sample) else f", +{len(sample) - len(shown)} more"
                    lines.append(f"    {label:6} {count:5}x  {shp:30} {', '.join(shown)}{more}")
                if label == "file":
                    exts = collections.Counter(
                        "".join(pathlib.PurePosixPath(n).suffixes) or "(none)" for n in group)
                    lines.append("    " + " ".join(f"{e}:{c}" for e, c in exts.most_common(8)))
        lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("listing")
    parser.add_argument("--depth", type=int, help="restrict to one depth and show every name")
    parser.add_argument("--max-examples", type=int, default=4)
    parser.add_argument("--loose", action="store_true",
                        help="ignore run lengths, so name families group more broadly")
    args = parser.parse_args(argv)
    listing = json.loads(pathlib.Path(args.listing).read_text())
    sys.stdout.write(survey(listing, args.depth, args.max_examples, widths=not args.loose))
    return 0


if __name__ == "__main__":
    sys.exit(main())
