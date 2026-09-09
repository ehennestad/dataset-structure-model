# extraction-methods

Every declarative extraction method and modifier on one layout: subject → fixed structural `data/` → session.

| Field | Method | Checks |
|-------|--------|--------|
| `subject_id` | `substring ":"` + `strip_prefix "sub-"` | normalize after extraction |
| `subject_letters` | `substring "4:6"` + `lowercase` | slice bounds, normalize |
| `session_datetime` | `regex` with group, `valueFormat "yyyy-MM-dd'T'HHmmss"` | LDML with a quoted literal → ISO datetime |
| `session_date` | `substring "0:10"`, `valueFormat "yyyy-MM-dd"` | ISO date |
| `session_time` | `substring "11:17"`, `valueFormat "HHmmss"` | ISO time |
| `session_number` | `regex "_s(\d+)$"`, `dataType integer` | typed value (JSON number) |
| `session_suffix` | `regex "s\d+$"` without a group; level given as index `2` | whole match; integer level reference |
| `session_id` | `template "{subject_id}_{session_date}_s{session_number}"` | composed after its inputs; ancestor field usable; integer formatted without padding |
| `rig` | `fixed` | constant |
| `relative_path` | `substring ":"` with `entityLayoutLevel: null` | whole relative path, no trailing slash |
| `experiment` | `regex` that never matches, `defaultValue "unknown"` | default applied, no issue |
| `notes_tag` | `regex` that never matches, no default | field absent, `extraction-failed` |

Also: the fixed level rejects `sub-CD02/raw/` (`no-match`); `sub-XY/` fails the subject pattern; a session's `metadata` carries the parent's identity field (`subject_id`) but not its other fields (`subject_letters`).
