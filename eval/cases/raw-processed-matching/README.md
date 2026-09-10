# raw-processed-matching

Listing from `conformance/raw-processed-matching`. The most important case in the set.

Two locations hold the same sessions under unrelated naming: `2025_05_23/2025_05_23_10_00_00_m110-20250523-001/` in `raw`, `subject-m110/session-m110-20250523-001/` in `processed`. Exactly one session (`m110-20250523-001`) exists in both.

`minMultiLocationEntities: 1` fails any config where that session comes out as two records instead of one with two `locations`. `forbiddenIssueCodes: ["metadata-conflict"]` fails one where the two locations extract different values for the same field. Together they are the check on the property `docs/guides/related-work.md` claims no other tool has: identity as a declared cross-store join key.

Also graded: a structural date level in `raw` (four sessions, not four date-entities); the one-sided entities (`-002` raw only, `-003` processed only, `m333` processed only) still appearing; session date and time read from the `raw` folder name.

**Not graded.** `maxNoMatch` is 3, matching the reference (`scratch/`, `notes.txt`, `calibration/`). `-003` has no date or time in the listing at all, so no value set is required of it.
