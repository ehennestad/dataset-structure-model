# inferred-ancestor-fields

One folder level of sessions named `<subject>-<sex>-<date>`. There are no subject folders, so every subject is inferred from its session names.

What it checks:

- An inferred ancestor carries **every** field of its type that the inferring paths yield, not only its identity: `subject_sex` is read from the session folder names and lands on the subject record, which still has `locations: []`.
- Values are pooled across all the descendants that infer the ancestor. `m110` has two sessions that agree (`F`). `m220` has one `F` and one `M` session: the reader keeps the first value in walk order (`m220-F-20250530/` sorts before `m220-M-20250524/`) and reports `metadata-conflict`.
- A field whose rule matches on no inferring path behaves as it does for an entity with its own paths: `subject_cohort` has no `defaultValue`, so it is absent and the subject carries `extraction-failed`.
- Sessions still receive only the parent's identity field (`subject_id`), not `subject_sex`.
