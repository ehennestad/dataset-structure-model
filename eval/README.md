# Skill Evaluation

`conformance/` checks a **reader**: same config, same listing, same records. This checks a **writer** — the skill that infers a config from a directory listing. A case gives the skill a `listing.json` and nothing else; the grader judges the config that comes back.

```bash
python eval/grade.py eval/cases/raw-processed-matching candidate.json
python eval/grade.py --reference          # every rubric, against a config known to satisfy it
```

---

## Why not compare records

The obvious design — run the skill's config through `dsm walk` and compare against the case's `expected.json` with `dsm compare` — fails good output.

In `folder-hierarchy-basic` the reference config extracts `session_id` as `baseline` from `20250523_baseline`, an identity that is not unique dataset-wide and is scoped by its subject parent. A skill given only the listing would very likely choose the whole folder name. Both configs are correct; their records differ. The same case plants a `_copy` folder to fire `duplicate-entity` and a second `.tif` to fire `cardinality-violation`, so a skill that sensibly excludes the copy is *penalised for being right*.

The conformance cases are adversarial reader fixtures, not datasets anyone would hand the skill. So the grader is blind to field naming, to identity values, and to which extraction method was used. It grades what the config **achieves** when walked.

## Entity-type names are slots, not names

A listing cannot tell you that `m110` is a "subject" rather than an "animal", a "cage" or
a "cohort". That is a semantic choice the skill puts to the user, so requiring a
particular word would fail a correct config.

A rubric therefore declares `entityTypes` as an **ordered list of labels**, outermost
first, and the grader resolves them against the candidate's own `entityTypes` in
declaration order — which the schema already pins to layout order. Every other rubric key
that names an entity type is read through that mapping. A config calling them
`animal`/`recording` is graded exactly like one calling them `subject`/`session`;
`tests/test_eval_grader.py` renames them in every case to keep it that way.

The count must match before anything else is comparable, so modelling one entity type
where two were expected fails at `entity types` and stops there.

## What a rubric may assert

| Key | Fails when |
|-----|-----------|
| `entityTypes` | The candidate declares a different number of entity types than the rubric has slots |
| `entityCounts` | The record count per type is outside the stated exact value or `[min, max]` range, or an unexpected entity type appears |
| `hierarchy` | A record's chain of entity-typed ancestors is not the stated one |
| `minEntitiesWithLocations` | Too few records of a type have a folder or files of their own — the entity was left to be inferred rather than modelled |
| `maxNoMatch` | More listing entries are unexplained (`no-match`) than allowed. `excluded` entries do not count: writing an `excludePattern` is the right answer |
| `minMultiLocationEntities` | Too few entities resolve to one record spanning more than one data location |
| `forbiddenIssueCodes` | The walk raises an issue code the case rules out |
| `metadataValueSets` | No distinct record of that type carries all the values in each listed set |
| `pathsMustNotShareRecord` | Two listed paths end up under one identity |
| *(always)* `listing identifiers resolve` | The config's `dataLocations[].identifier` / `rootStoragePaths[].identifier` are not the ones the listing was built with |

Every value is a floor or a ceiling, never an exact transcript. A skill that finds more structure than the reference still passes.

## Skill rules versus rubric checks

Two checks are about what the **skill** may emit rather than about what a good config looks like:

- `forbidFunctionExtractors` — `function` needs an implementation in every reader (AGENTS.md).
- `forbidPathTemplate` — a read-only listing cannot confirm a write convention.

A hand-written config may legitimately do both, so `--reference` reports them as notes rather than failures. Grading a candidate applies them normally.

## Cases

| Case | What it is for |
|------|----------------|
| `folder-hierarchy-basic` | Two folder levels, noise to exclude, a duplicate folder the skill may read either way |
| `flat-session-files` | File-level entities in one flat folder, and the `-001` / `-0010` substring-collision trap |
| `raw-processed-matching` | Two locations, unrelated naming, one entity set — the property DSM exists for |
| `extraction-methods` | A structural level mid-tree and a sibling that must not match |
| `function-extractor` | A value the reader fixture reads with a registry function; a regex must do instead |

Each case's `README.md` states what is graded and, as importantly, what is deliberately left free.

## Trusting the rubrics

Two things keep them honest, both in `tests/test_eval_grader.py`:

1. **Every rubric is satisfied by a reference config.** `referenceConfig` points at the case's conformance config, or at a local `reference.json` where that config would fail its own rubric — `function-extractor`'s does, by using a function. A rubric nobody has satisfied might be impossible.
2. **Every check has a test that breaks a reference config and asserts the check fires.** A grader that passes everything is worth nothing.

Three corrections came out of actually running it, which is the argument for building the
harness before the skill:

1. Making the subject level structural does *not* flatten the hierarchy — the walker infers
   the ancestor from the still-extracted `subject_id`, as `docs/guides/conformance.md`
   specifies. What it loses is the subject's folder, which nothing graded until
   `minEntitiesWithLocations` was added.
2. Grading was not naming-blind after all: rubric keys named entity types directly, so a
   correct config calling them `animal`/`recording` failed. Hence slots.
3. A config whose location identifiers differ from the listing's raised a bare `KeyError`
   out of the walker. The grader now reports it as a check. The underlying reader crash is
   recorded in the work item and is not fixed here.

## Adding a case

1. `eval/cases/<kebab-name>/` with `listing.json`, `rubric.json`, `README.md`.
2. Assert only what the listing determines. When two readings are defensible, use a range and say so in the README.
3. Point `referenceConfig` at a config that satisfies the rubric; write one locally if none exists.
4. `python eval/grade.py --reference` must pass, and `pytest tests/test_eval_grader.py` must still pass.
