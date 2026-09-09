# Entity Record

A DSM config says how to *read* a dataset. The **entity record** says what comes out: the object a reader emits for each entity it discovers. It is defined by [`schema/EntityRecord.schema.json`](https://github.com/ehennestad/dataset-structure-model/blob/main/schema/EntityRecord.schema.json) and is the interchange format between readers in different languages and the tools that build entity tables from them. Two readers given the same config and the same directory tree produce the same records.

```json
{
  "entityType": "session",
  "identity": { "session_id": "m110-20250510-001" },
  "parents": [
    { "entityType": "subject", "identity": { "subject_id": "m110" } }
  ],
  "locations": [
    {
      "dataLocationIdentifier": "recorded",
      "rootStoragePathIdentifier": "lab-nas",
      "fileSystemType": "file",
      "paths": ["m110-20250510-001_raw.tif", "m110-20250510-001_meta.json"],
      "files": {
        "raw_movie": ["m110-20250510-001_raw.tif"],
        "metadata": ["m110-20250510-001_meta.json"]
      },
      "isComplete": true
    }
  ],
  "metadata": {
    "session_id": "m110-20250510-001",
    "subject_id": "m110",
    "session_date": "2025-05-10"
  }
}
```

## Fields

| Field | Required | Description |
|-------|----------|-------------|
| `entityType` | Yes | Name from `entityTypes` |
| `identity` | Yes | The entity's own identity field(s) and value(s) |
| `parents` | No | Identity of each entity-typed ancestor, outermost first; structural levels do not appear. `identity` + `parents` is the full key. |
| `locations` | Yes (≥1) | Where the entity was found; one entry per data location. An entity matched across locations has several. |
| `metadata` | No | Every extracted field for this entity, keyed by definition key |
| `issues` | No | Human-readable problems a reader found for this entity |

Each `locations` entry:

| Field | Required | Description |
|-------|----------|-------------|
| `dataLocationIdentifier` | Yes | `identifier` of the data location |
| `rootStoragePathIdentifier` | Yes | `identifier` of the root path the entity was found under |
| `fileSystemType` | No | `folder` (default) or `file` |
| `paths` | Yes (≥1) | Relative to the root, `/`-separated. One folder path for a folder entity; the set of file paths for a file entity. |
| `files` | No | Files matched per **named** `filePatterns` entry |
| `isComplete` | No | `true` when every `isRequired` pattern matched |

`date`, `time` and `datetime` values are ISO 8601 strings.

## Why it is part of the spec

Without it, "supports multiple entity tables" and "portable across languages" are claims nobody can check. With it, conformance is a fixture: a directory listing plus the records a reader must produce. A tool that stores where each entity lives (a session table, for example) stores exactly this object.
