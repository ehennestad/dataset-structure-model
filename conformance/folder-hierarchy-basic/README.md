# folder-hierarchy-basic

Two folder levels (subject → session), `substring` and `regex` extraction, a date with `valueFormat`, `excludePatterns`, and `filePatterns` with `isRequired` and `cardinality`.

What it checks:

- Session identity includes the parent: `baseline` under `m110` and `baseline` under `m220` are two sessions.
- `m110/20250601_stim` has two `.tif` files for a `cardinality: one` pattern → `cardinality-violation`, both files reported.
- `m220/20250524_baseline` lacks the required movie → `isComplete: false`, `missing-required-file`.
- `m220/20250524_baseline_copy` extracts the same `session_id` as `m220/20250524_baseline` → one record with two paths and `duplicate-entity`.
- `sub/x.dat` inside a session folder is covered by the session (innermost level); it is not unmatched.
- `.DS_Store` and `temp/` hit `excludePatterns` → unmatched with reason `excluded`; `m110/README.txt` is a file where session folders are expected → `no-match`.
