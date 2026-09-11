# extraction-methods

Every declarative extraction method and modifier on one layout: subject → fixed structural `data/` → session.

| Field | Method | Checks |
|-------|--------|--------|
| `subject_id` | `substring ":"` + `strip_prefix "sub-"` | normalize after extraction |
| `subject_letters` | `substring "4:6"` + `lowercase` | slice bounds, normalize |
| `session_datetime` | `regex` with group, `valueFormat "yyyy-MM-dd'T'HHmmss"` | LDML with a quoted literal → ISO datetime |
| `session_date` | `substring "0:10"`, `valueFormat "yyyy-MM-dd"` | ISO date |
| `session_date_short` | `regex` dropping the century, `valueFormat "yy-MM-dd"` | two-digit year; `69-01-01` → `1969-01-01` pins the 1969–2068 pivot |
| `session_time` | `substring "11:17"`, `valueFormat "HHmmss"` | ISO time |
| `session_number` | `regex "_s(\d+)$"`, `dataType integer` | typed value (JSON number) |
| `session_suffix` | `regex "s\d+$"` without a group; level given as index `2` | whole match; integer level reference |
| `session_id` | `template "{subject_id}_{session_date}_s{session_number}"` | composed after its inputs; ancestor field usable; integer formatted without padding |
| `rig` | `fixed` | constant |
| `relative_path` | `substring ":"` with `entityLayoutLevel: null` | whole relative path, no trailing slash |
| `experiment` | `regex` that never matches, `defaultValue "unknown"` | default applied, no issue |
| `notes_tag` | `regex` that never matches, no default | field absent, `extraction-failed` |

The session `2069-01-01T000000_s2` exists for the pivot: `session_date` reads the full year (2069) while `session_date_short` reads `69` and must give 1969, the same answer Python's `strptime` and MATLAB `datetime` with `PivotYear` 1969 produce.

Also: the fixed level rejects `sub-CD02/raw/` (`no-match`); `sub-XY/` fails the subject pattern; a session's `metadata` carries the parent's identity field (`subject_id`) but not its other fields (`subject_letters`).
