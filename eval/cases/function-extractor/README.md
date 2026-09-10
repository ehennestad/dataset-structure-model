# function-extractor

Listing from `conformance/function-extractor`. The reader fixture reads the session number through a registry function; AGENTS.md forbids the skill from emitting `function` by default, so this case checks it reaches the same result declaratively.

`^ses-(\d+)` does the job: `ses-1` → 1, `ses-2_extra` → 2, `ses-pilot` → no match. The grader's default `forbidFunctionExtractors` rejects a `function` rule outright, and `forbiddenIssueCodes: ["unresolved-extractor"]` catches the variant that emits one and leaves it unregistered.

`referenceConfig` points at `reference.json` in this directory rather than the conformance config, which would fail its own rubric by using a function. That local config is the proof the rubric is achievable without one.

**Not graded.** `ses-pilot` has no session number. The reference gives it none and the rubric asks only that 1 and 2 appear, so an `integer` typing that drops it is fine.
