# Dataset Structure Model

**A JSON Schema standard for declaratively describing the structure of scientific datasets.**

The Dataset Structure Model (DSM) is a machine-actionable configuration format that captures how a scientific dataset is organised on disk — its folder hierarchy, entity types (subjects, sessions, recordings), naming conventions, and metadata extraction rules. It acts as a shared contract between researchers, tools, and AI agents.

---

## What problem does it solve?

Scientific datasets are notoriously heterogeneous. Raw data might live at `D:\Data\TwoPhoton\m110\20250523_session1\rec01\`, while processed data for the same session is at `/Volumes/DataDrive/Processed/m110\20250523_session1\processed\`. Tools need to understand both, know they refer to the same session, and know where to write derived outputs.

Without a formal description, every tool hardcodes assumptions about folder structure. With DSM, tools read a single config file that answers:

- **Where** is the data? (per environment, per storage type)
- **What** is the folder hierarchy? (subjects → sessions → recordings)
- **How** are entity identities extracted from folder names? (regex, substring, fixed value)
- **How** do entities in different locations correspond to each other?
- **What** files live inside each entity folder, and what is each file's role?

---

## Key features

- **Descriptive, not prescriptive** — describes your data as it exists; no reorganisation required
- **Multi-location** — a single config describes raw, processed, and derived data in separate folder trees
- **Cross-location entity matching** — declares how entities (e.g. sessions) are linked across locations with different naming conventions
- **Metadata-aware** — extraction rules pull metadata from folder/file names via regex, substring, or custom functions
- **Multi-environment** — same dataset, different root paths for Windows lab, Mac analysis station, HPC cluster
- **LLM-ready** — structured and self-describing; suitable as direct input to AI agents and pipelines
- **Pipeline-friendly** — integrates naturally with Nextflow, Snakemake, and similar tools

---

## Quick example

```json
{
  "schemaVersion": "1.0.0",
  "entityTypes": [
    { "name": "subject", "identifierRef": "subject_id" },
    { "name": "session", "identifierRef": "session_id" }
  ],
  "metadataDefinitions": {
    "subject_id": { "name": "Subject ID", "ofEntity": "subject", "dataType": "string" },
    "session_id": { "name": "Session ID", "ofEntity": "session", "dataType": "string" }
  },
  "dataLocations": [{
    "identifier": "raw-data",
    "dataCategory": "raw",
    "rootStoragePaths": [{ "identifier": "lab", "path": "/data/raw", "environment": "linux-lab" }],
    "entityLayout": [
      { "name": "subjects", "entityType": "subject", "matchPattern": "^[A-Za-z0-9]+$" },
      { "name": "sessions", "entityType": "session", "matchPattern": "^\\d{8}_.*$" }
    ],
    "metadataMapping": [
      { "metadataRef": "subject_id", "extraction": { "method": "substring", "pattern": "0:end", "entityLayoutLevel": 0 } },
      { "metadataRef": "session_id", "extraction": { "method": "regex", "pattern": "^\\d{8}_(.+)$", "entityLayoutLevel": 1 } }
    ]
  }],
  "preferences": {
    "defaultDataLocationIdentifier": "raw-data",
    "environmentIdentifier": "linux-lab"
  }
}
```

---

## Navigation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Quick Start](getting-started/quickstart.md)**

    Get a valid DSM config in minutes

- :material-book-open: **[Core Concepts](getting-started/concepts.md)**

    Understand entities, layouts, and metadata extraction

- :material-file-code: **[Schema Reference](reference/index.md)**

    Complete reference for every field and definition

- :material-lightbulb: **[Examples](examples/index.md)**

    Annotated real-world configs for neuroscience and clinical trials

</div>

---

## No equivalent standard exists

DSM fills a gap in the scientific data management ecosystem. Existing standards are either prescriptive (you must reorganise your data to conform) or focused on tabular/file-level metadata rather than folder hierarchy and entity semantics. See the [Design Decisions](guides/design-decisions.md) guide for details.
