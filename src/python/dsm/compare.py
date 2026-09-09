"""Compare two walk results by the conformance comparison rules (docs/guides/conformance.md)."""
from typing import List


def record_key(record: dict):
    return (record["entityType"],
            tuple(sorted(record["identity"].items())),
            tuple((p["entityType"], tuple(sorted(p["identity"].items()))) for p in record.get("parents", [])))


def _label(key):
    entity_type, identity, parents = key
    ident = ", ".join(f"{k}={v}" for k, v in identity)
    chain = " < ".join(f"{t}({', '.join(f'{k}={v}' for k, v in i)})" for t, i in parents)
    return f"{entity_type}({ident})" + (f" under {chain}" if chain else "")


def compare_results(expected: dict, actual: dict) -> List[str]:
    """Differences between an expectation and a reader's result; empty when the reader passes."""
    diffs: List[str] = []
    if "error" in expected or "error" in actual:
        exp_code = expected.get("error", {}).get("code")
        act_code = actual.get("error", {}).get("code")
        if exp_code != act_code:
            diffs.append(f"error code: expected {exp_code!r}, got {act_code!r}")
        return diffs

    exp = {record_key(r): r for r in expected.get("records", [])}
    act = {record_key(r): r for r in actual.get("records", [])}
    for key in sorted(set(exp) - set(act), key=str):
        diffs.append(f"missing record {_label(key)}")
    for key in sorted(set(act) - set(exp), key=str):
        diffs.append(f"unexpected record {_label(key)}")
    for key in sorted(set(exp) & set(act), key=str):
        diffs += [f"{_label(key)}: {d}" for d in _compare_record(exp[key], act[key])]

    exp_unmatched = {(u["dataLocationIdentifier"], u["rootStoragePathIdentifier"], u["path"], u["reason"])
                     for u in expected.get("unmatched", [])}
    act_unmatched = {(u["dataLocationIdentifier"], u["rootStoragePathIdentifier"], u["path"], u["reason"])
                     for u in actual.get("unmatched", [])}
    for item in sorted(exp_unmatched - act_unmatched):
        diffs.append(f"missing unmatched {item[0]}/{item[1]} {item[2]} ({item[3]})")
    for item in sorted(act_unmatched - exp_unmatched):
        diffs.append(f"unexpected unmatched {item[0]}/{item[1]} {item[2]} ({item[3]})")
    return diffs


def _compare_record(expected: dict, actual: dict) -> List[str]:
    diffs: List[str] = []
    exp_locs = {(l["dataLocationIdentifier"], l["rootStoragePathIdentifier"]): l for l in expected.get("locations", [])}
    act_locs = {(l["dataLocationIdentifier"], l["rootStoragePathIdentifier"]): l for l in actual.get("locations", [])}
    for key in sorted(set(exp_locs) - set(act_locs)):
        diffs.append(f"missing location {key[0]}/{key[1]}")
    for key in sorted(set(act_locs) - set(exp_locs)):
        diffs.append(f"unexpected location {key[0]}/{key[1]}")
    for key in sorted(set(exp_locs) & set(act_locs)):
        e, a = exp_locs[key], act_locs[key]
        where = f"{key[0]}/{key[1]}"
        if e.get("fileSystemType", "folder") != a.get("fileSystemType", "folder"):
            diffs.append(f"{where}: fileSystemType expected {e.get('fileSystemType', 'folder')}, got {a.get('fileSystemType', 'folder')}")
        if sorted(e["paths"]) != sorted(a["paths"]):
            diffs.append(f"{where}: paths expected {sorted(e['paths'])}, got {sorted(a['paths'])}")
        if ("files" in e) != ("files" in a):
            diffs.append(f"{where}: files {'expected' if 'files' in e else 'not expected'}")
        elif "files" in e:
            for name in sorted(set(e["files"]) | set(a["files"])):
                if sorted(e["files"].get(name, [])) != sorted(a["files"].get(name, [])):
                    diffs.append(f"{where}: files[{name}] expected {sorted(e['files'].get(name, []))}, got {sorted(a['files'].get(name, []))}")
        if e.get("isComplete") != a.get("isComplete"):
            diffs.append(f"{where}: isComplete expected {e.get('isComplete')}, got {a.get('isComplete')}")

    exp_meta, act_meta = expected.get("metadata", {}), actual.get("metadata", {})
    for field in sorted(set(exp_meta) | set(act_meta)):
        if field not in act_meta:
            diffs.append(f"metadata[{field}] missing (expected {exp_meta[field]!r})")
        elif field not in exp_meta:
            diffs.append(f"metadata[{field}] unexpected ({act_meta[field]!r})")
        elif exp_meta[field] != act_meta[field]:
            diffs.append(f"metadata[{field}] expected {exp_meta[field]!r}, got {act_meta[field]!r}")

    exp_codes = {i["code"] for i in expected.get("issues", [])}
    act_codes = {i["code"] for i in actual.get("issues", [])}
    if exp_codes != act_codes:
        diffs.append(f"issues expected {sorted(exp_codes)}, got {sorted(act_codes)}")
    return diffs
