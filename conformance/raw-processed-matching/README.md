# raw-processed-matching

Config: identical to `examples/raw_processed_two_photon.json`. Two locations with different hierarchies, listed on the `mac-analysis` environment.

What it checks:

- **Structural level**: `dates` has no `entityType`; a session reads `session_date` from it (`substring ":"` with `valueFormat yyyy_MM_dd`) but it plays no part in identity.
- **Cross-location matching**: raw `2025_05_23/2025_05_23_10_00_00_m110-20250523-001` and processed `subject-m110/session-m110-20250523-001` yield the same `session_id` under the same subject → one record with two `locations`; `metadata` is the union (date and time only come from raw).
- **One-sided entities**: session `002` exists only in raw, `003` only in processed; each has one location and no issue.
- **Ancestor from descendant**: raw has no subject level, so `subject_id` read from session names identifies the parent. `m222` has no folder anywhere → `locations: []`. `m110` and `m333` have folders in processed.
- **Derived matchPattern**: the processed `sessions` level has only `pathComponentTemplate: session-{session_id}`; the pattern derived from `session_id`'s `validation.pattern` matches `session-m110-20250523-001` and rejects `scratch`.
- **additionalFolders**: `logs/` inside a session is covered by the session.
- `2025_05_23/notes.txt`, `calibration/` and `subject-m110/scratch/` are `no-match`.
