# folder-hierarchy-basic

Listing from `conformance/folder-hierarchy-basic`. The skill sees `listing.json` only.

Graded: two subjects (so `temp/` and `.DS_Store` must be excluded, not counted); sessions parented by subject; the three session dates read out of the folder names as ISO dates.

**Not graded, deliberately.** The session count is a range `[3, 4]`. `m220/20250524_baseline_copy/` is a duplicate the reference config lets collide into one `duplicate-entity` record; a skill that instead excludes `_copy` or treats it as its own session is also right. Identity naming is likewise free: the reference extracts `baseline` from `20250523_baseline`, but the whole folder name is an equally good identity — so nothing here grades the identity *value*.

`maxNoMatch` is 1, the reference's own result (`m110/README.txt`). A skill that excludes it too does better and still passes.
