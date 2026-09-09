"""Human-readable dry-run report for a walk."""
from collections import Counter
from typing import List

from .config import Config
from .records import WalkResult


def render_report(config: Config, result: WalkResult) -> str:
    lines: List[str] = []
    lines.append(f"Config: {config.source or '<memory>'} (valid)")
    lines.append(f"Environment: {result.environment or '-'}")
    for warning in result.warnings:
        lines.append(f"Warning: {warning}")
    lines.append("Roots:")
    for loc_id, root_id, count in result.roots:
        lines.append(f"  {loc_id}/{root_id}: {count} entries")

    lines.append("Entities:")
    for entity_type in config.entity_types:
        records = [r for r in result.records if r.entity_type == entity_type]
        inferred = sum(1 for r in records if not r.locations)
        note = f" ({inferred} without a folder or files of their own)" if inferred else ""
        lines.append(f"  {entity_type}: {len(records)}{note}")

    codes = Counter(issue.code for r in result.records for issue in r.issues)
    lines.append("Issues: " + (", ".join(f"{code}: {n}" for code, n in sorted(codes.items())) if codes else "none"))
    for record in result.records:
        for issue in record.issues:
            ident = ", ".join(f"{k}={v}" for k, v in record.identity.items())
            lines.append(f"  {record.entity_type}({ident}): {issue.code} - {issue.message}")

    lines.append("Unresolved extractors: " + (", ".join(sorted(result.unresolved_extractors)) or "none"))

    lines.append(f"Unmatched: {len(result.unmatched)}")
    for item in result.unmatched:
        detail = f"  ({item.detail})" if item.detail else ""
        lines.append(f"  {item.data_location}/{item.root_storage_path}  {item.path}  {item.reason}{detail}")
    return "\n".join(lines) + "\n"
