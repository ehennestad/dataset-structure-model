# AI Agent Instructions

This page provides instructions for AI agents (LLMs) generating valid Dataset Structure Model configuration files. It is written to be self-contained: an agent can follow it without access to the schema file itself.

!!! note "Work in progress"
    This page will be expanded in a future release with a comprehensive prompt-ready specification. The current content covers the most important rules for producing valid instances.

---

## What the DSM is

A DSM configuration is a single JSON file that describes the physical layout and semantic structure of a scientific dataset. It is **descriptive** — it records how data is already organised on disk, rather than prescribing how it should be organised.

The file must validate against `DatasetStructureModel.schema.json` (JSON Schema draft-07).

---

## Required top-level keys

| Key | Type | Description |
|-----|------|-------------|
| `schemaVersion` | string | Always `"1.0.0"` for the current schema |
| `entityTypes` | array | One entry per semantic entity type in the dataset |
| `metadataDefinitions` | object | Global vocabulary of metadata fields |
| `dataLocations` | array | One entry per logical collection of data |

Optional top-level keys: `entityRelationships`, `preferences`.

---

## `entityTypes` — rules

- Each entry must have `"name"` (string, required).
- Add `"identifierRef"` (string) naming the `metadataDefinitions` key that uniquely identifies this entity across locations. This enables cross-location entity matching.
- Do **not** put `entityRelationships` inside an `entityType` or inside a `dataLocation` — they belong at the top level.
- Valid optional fields: `name`, `description`, `isPrimary`, `identifierRef`, `identifierRefs`. No other fields are allowed (`additionalProperties: false`).

```json
"entityTypes": [
  { "name": "subject", "isPrimary": true, "identifierRef": "subject_id" },
  { "name": "session", "identifierRef": "session_id" }
]
```

---

## `metadataDefinitions` — rules

- This is an **object** (not an array). Keys are metadata field identifiers (e.g. `"subject_id"`).
- Each value must have: `"name"` (string), `"dataType"` (string), `"ofEntity"` (string matching an entityType name).
- `"dataType"` must be one of: `string`, `number`, `integer`, `boolean`, `date`, `datetime`.
- Do **not** put `"ofEntity"` or extraction rules in `metadataMapping` — put `"ofEntity"` here.

```json
"metadataDefinitions": {
  "subject_id": {
    "name": "Subject ID",
    "dataType": "string",
    "ofEntity": "subject",
    "description": "Unique identifier for research subjects"
  }
}
```

---

## `dataLocations` — rules

Each entry must have:

| Field | Type | Notes |
|-------|------|-------|
| `identifier` | string | Unique ID for this location |
| `displayName` | string | Human-readable name |
| `dataCategory` | string | See enum below |
| `rootStoragePaths` | array | At least one entry |
| `entityLayout` | array | At least one level |
| `metadataMapping` | array | One entry per metadata field extracted here |

`dataCategory` must be one of: `raw`, `processed`, `derived`, `imported`, `reference`, `temporary`, `archive`, `custom`.

Optional fields: `description`, `derivedFrom`, `tags`, `customProperties`, `pathTemplate`.

**Do not** put `entityRelationships` inside a `dataLocation`.

---

## `rootStoragePaths` — rules

Each entry must have `"identifier"`, `"path"` (string), and `"storageType"`.

`storageType` must be one of: `local`, `network`, `cloud`, `external`.

Optional: `volumeName`, `environment`, `priority` (integer), `isAvailable` (boolean).

---

## `entityLayout` — rules

- An **array** in order from outermost to innermost folder level (level 0 = top).
- Each entry must have `"name"` (string), `"entityType"` (string matching an entityType name or `"other"`).
- `"matchPattern"` (regex string) is required unless `"pathComponentTemplate"` is present.
- `"isVariable": true` means folder names vary per entity; `false` means fixed name.
- When `"isVariable": false`, add `"fixedName"` with the exact folder name.
- For derived locations, use `"pathComponentTemplate"` (e.g. `"session-{session_id}"`) to support folder name generation.

---

## `filePatterns` in `entityLayout` levels

Each entry in `filePatterns` is a **file class**. Required fields: `"pattern"` (regex), `"role"`.

`role` must be one of: `primary`, `sidecar`, `qc`, `log`, `config`, `auxiliary`.

Optional: `format` (MIME type string), `description`, `isRequired` (boolean), `groupKey` (string), `metadataExtractors` (array).

---

## `metadataMapping` — rules

- An **array** (not an object).
- Each entry must have `"metadataRef"` (string — key from `metadataDefinitions`) and `"extraction"` (object).
- `extraction` must have `"method"`. Valid methods: `substring`, `regex`, `function`, `template`, `fixed`, `filename`, `filepath`.
- `"entityLayoutLevel"` (integer, zero-based) specifies which folder depth to extract from.
- Do **not** put `"ofEntity"` here — it belongs in `metadataDefinitions`.
- Valid optional fields on each item: `metadataRef`, `extraction`. No other fields are allowed.

---

## `entityRelationships` — rules

- Top-level array only. **Never** inside `dataLocation` or `entityType`.
- Each entry must have `"sourceEntity"`, `"targetEntity"`, `"relationType"`.
- `relationType` must be one of: `oneToOne`, `oneToMany`, `manyToOne`, `manyToMany`.
- Optional: `relationName`, `description`.
- No other fields are allowed (`additionalProperties: false`).

---

## Common mistakes to avoid

1. Putting `entityRelationships` inside a `dataLocation` — it must be at the top level.
2. Putting `"ofEntity"` inside `metadataMapping` entries — it belongs in `metadataDefinitions`.
3. Using `"role": "derived"` in a file class — `derived` is a `dataCategory` value, not a file role.
4. Adding extra properties to objects that have `additionalProperties: false` — `entityType`, `entityRelationship`, `metadataMapping` items, `preferences` are strict.
5. Making `metadataMapping` an object instead of an array.
6. Omitting `entityLayoutLevel` in extraction rules — tools need this to know which folder depth to parse.

---

## Minimal valid example

```json
{
  "schemaVersion": "1.0.0",
  "entityTypes": [
    { "name": "subject", "isPrimary": true, "identifierRef": "subject_id" },
    { "name": "session", "identifierRef": "session_id" }
  ],
  "entityRelationships": [
    {
      "sourceEntity": "subject",
      "targetEntity": "session",
      "relationType": "oneToMany"
    }
  ],
  "metadataDefinitions": {
    "subject_id": {
      "name": "Subject ID",
      "dataType": "string",
      "ofEntity": "subject"
    },
    "session_id": {
      "name": "Session ID",
      "dataType": "string",
      "ofEntity": "session"
    }
  },
  "dataLocations": [
    {
      "identifier": "raw-data",
      "displayName": "Raw Data",
      "dataCategory": "raw",
      "rootStoragePaths": [
        {
          "identifier": "main",
          "path": "/data/raw",
          "storageType": "local",
          "environment": "linux-server"
        }
      ],
      "entityLayout": [
        {
          "name": "subjects",
          "entityType": "subject",
          "matchPattern": "^[A-Za-z0-9]+$",
          "isRequired": true,
          "isVariable": true
        },
        {
          "name": "sessions",
          "entityType": "session",
          "matchPattern": "^\\d{8}_[A-Za-z0-9]+$",
          "isRequired": true,
          "isVariable": true
        }
      ],
      "metadataMapping": [
        {
          "metadataRef": "subject_id",
          "extraction": { "method": "substring", "pattern": "0:end", "entityLayoutLevel": 0 }
        },
        {
          "metadataRef": "session_id",
          "extraction": { "method": "substring", "pattern": "0:end", "entityLayoutLevel": 1 }
        }
      ]
    }
  ],
  "preferences": {
    "defaultDataLocationIdentifier": "raw-data",
    "environmentIdentifier": "linux-server"
  }
}
```

---

## Validation

```bash
pip install jsonschema
python -m jsonschema -i my-dataset.json schema/DatasetStructureModel.schema.json
```

A zero exit code means the file is valid.
