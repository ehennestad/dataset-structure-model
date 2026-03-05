# Development Guide

This guide covers the tools and workflow for contributing to the Dataset Structure Model.

---

## Setup

**Requirements:** Python 3.9+, `pip`

```bash
# Clone the repository
git clone https://github.com/ehennestad/dataset-structure-model.git
cd dataset-structure-model

# Install documentation dependencies
pip install -r requirements-docs.txt

# Install test dependencies
pip install -r requirements-test.txt
```

---

## Validating examples

To check that an example file is valid against the schema:

```bash
python -m jsonschema -i examples/neuroscience_dataset_example.json schema/DatasetStructureModel.schema.json
python -m jsonschema -i examples/clinical_trial_example.json schema/DatasetStructureModel.schema.json
```

A zero exit code means the file is valid.

To run the full test suite:

```bash
pytest tests/ -v
```

---

## Building the documentation

**Serve locally with live reload:**

```bash
mkdocs serve
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. Changes to `.md` files are reflected immediately.

**Build and check for warnings:**

```bash
mkdocs build --strict
```

`--strict` treats warnings as errors. The build must pass with zero warnings before a documentation change is merged.

The built site is written to `site/` (git-ignored).

---

## Schema update checklist

Follow these steps whenever making changes to `schema/DatasetStructureModel.schema.json`:

1. **Update the schema** — make your changes to `schema/DatasetStructureModel.schema.json`.
2. **Bump `schemaVersion`** in all example files if the change is breaking.
3. **Add a CHANGELOG entry** — add the change under `## [Unreleased]` in `CHANGELOG.md`.
4. **Run validation** — `pytest tests/ -v` must pass.
5. **Update affected reference pages** — update `docs/reference/` pages that document the changed properties.
6. **Update the AI agent instructions** — if enum values, required fields, or `additionalProperties` rules changed, update `docs/guides/ai-agent-instructions.md`.
7. **If new examples are needed**, create them in `examples/` and add an annotated walkthrough in `docs/examples/`.

---

## Schema versioning policy

This project uses [Semantic Versioning](https://semver.org/):

- **Patch** (`1.0.x`) — documentation fixes, description improvements, no schema changes.
- **Minor** (`1.x.0`) — additive schema changes: new optional fields, new enum values. Existing valid configs remain valid.
- **Major** (`x.0.0`) — breaking changes: removed or renamed fields, new required fields, changed `additionalProperties` rules.

The `schemaVersion` field in config files should match the minor version they were written for (e.g. `"1.0.0"` for any `1.0.x` schema).

---

## Repository structure

```
dataset-structure-model/
├── schema/
│   └── DatasetStructureModel.schema.json   ← the schema (source of truth)
├── examples/
│   ├── neuroscience_dataset_example.json
│   └── clinical_trial_example.json
├── docs/                                    ← MkDocs documentation source
│   ├── index.md
│   ├── getting-started/
│   ├── reference/
│   ├── guides/
│   ├── examples/
│   ├── api/
│   └── contributing/
├── tests/                                   ← pytest test suite
├── src/
│   ├── python/                              ← Python API (in development)
│   └── matlab/                              ← MATLAB API (in development)
├── mkdocs.yml
├── requirements-docs.txt
├── requirements-test.txt
├── CHANGELOG.md
└── LICENSE
```
