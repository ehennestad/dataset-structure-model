# flat-session-files

Config: identical to `examples/flat_session_files.json`. One `file` level: every session's files sit in the root folder.

What it checks:

- Files are grouped into sessions by extracted `session_id`: six files → one session `m110-20250510-001`.
- `paths` holds every file whose identity is the session's, including `_extra.bin` and `_raw.tif.bak` which no `filePatterns` entry matches; `files` holds only the named-pattern matches. `_raw.tif.bak` does not match `^{session_id}_raw\.tif$` because the pattern is anchored.
- Session `003` has only a `_meta.json` → `isComplete: false`, `missing-required-file`.
- `subject_id` is read from the file names (`substring 0:4`); subjects have no folder of their own → subject records with `locations: []`.
- `m110-20250510-0010_raw.tif` does not match the level's `matchPattern` (`\d{3}_`) → `no-match`; `.DS_Store` → `excluded`; `notes.txt` → `no-match`.
