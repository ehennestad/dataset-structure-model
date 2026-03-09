# Schema Usage Guide

This guide explains how to write a Dataset Structure Model (DSM) configuration for your dataset. It walks through each section of the schema with practical examples and links to the full reference documentation.

---

## Overview

A DSM configuration is a single JSON file that describes:

- **What entity types** exist in your dataset (subjects, sessions, recordings, …)
- **How entities relate** to each other (a subject has many sessions)
- **Where data lives** on disk (one or more storage paths per environment)
- **How folders are laid out** within each data location
- **How metadata is extracted** from folder and file names
- **How to identify the same entity** across different data locations

The configuration is purely descriptive — it tells tools how to read your data, not how to organise it. Your files do not need to move.

A minimal valid configuration looks like this:

```json
{
  "schemaVersion": "1.0.0",
  "entityTypes": [
    { "name": "subject" },
    { "name": "session" }
  ],
  "metadataDefinitions": {
    "subject_id": {
      "name": "Subject ID",
      "dataType": "string",
      "ofEntity": "subject"
    }
  },
  "dataLocations": [
    {
      "identifier": "raw-data",
      "displayName": "Raw Data",
      "dataCategory": "raw",
      "sourceType": "filesystem",
      "filesystemSource": {
        "rootStoragePaths": [
          { "identifier": "main", "path": "/data/raw", "storageType": "local" }
        ],
        "entityLayout": [
          { "name": "subjects", "entityType": "subject", "matchPattern": "^[A-Za-z0-9]+$", "isVariable": true }
        ],
        "metadataMapping": [
          {
            "metadataRef": "subject_id",
            "extraction": { "method": "substring", "pattern": "0:end", "entityLayoutLevel": 0 }
          }
        ]
      }
    }
  ]
}
```

See the [Schema Reference → Overview](../reference/overview.md#required-properties) for a full property table.

---

## Entity Types

[Entity types](../reference/overview.md#entitytypes) are the semantic categories of things in your dataset. Declare them once at the top level.

```json
"entityTypes": [
  {
    "name": "subject",
    "description": "A research subject (mouse)",
    "isPrimary": true,
    "identifierRef": "subject_id"
  },
  {
    "name": "session",
    "description": "A single experimental recording session",
    "identifierRef": "session_id"
  }
]
```

The `identifierRef` field names a key in `metadataDefinitions` that uniquely identifies an entity of this type. Tools use this to match entities across different data locations — for example, to find which processed files correspond to a given raw recording. See [Cross-Location Entity Matching](#cross-location-entity-matching) below.

If `isPrimary` is true, this entity type is the top-level unit of your dataset (typically the subject or participant level).

---

## Entity Relationships

[Entity relationships](../reference/entity-relationships.md) are declared at the top level and apply globally across all data locations.

```json
"entityRelationships": [
  {
    "sourceEntity": "subject",
    "targetEntity": "session",
    "relationType": "oneToMany",
    "relationName": "hasSessions",
    "description": "A subject can have multiple recording sessions"
  }
]
```

Valid `relationType` values: `oneToOne`, `oneToMany`, `manyToOne`, `manyToMany`.

The relationships describe the semantic structure of your data — they do not have to mirror the physical folder hierarchy. If sessions from all subjects are stored in one flat folder, the `oneToMany` relationship still correctly models that one subject has many sessions.

---

## Metadata Definitions

[Metadata definitions](../reference/metadata-definitions.md) are a global vocabulary of metadata fields. Define each field once here; data locations reference them by key.

```json
"metadataDefinitions": {
  "subject_id": {
    "name": "Subject ID",
    "ofEntity": "subject",
    "dataType": "string",
    "description": "Unique identifier for research subjects",
    "validation": {
      "pattern": "^[A-Za-z0-9]+$",
      "minLength": 3
    }
  },
  "acquisition_date": {
    "name": "Acquisition Date",
    "ofEntity": "session",
    "dataType": "date",
    "description": "Date when the session data was acquired"
  },
  "imaging_depth": {
    "name": "Imaging Depth",
    "ofEntity": "recording",
    "dataType": "number",
    "unit": "µm",
    "description": "Depth of the imaging plane below the cortical surface",
    "validation": { "minimum": 0, "maximum": 1000 }
  }
}
```

Key fields:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Human-readable display name |
| `ofEntity` | Yes | Which entity type this field describes |
| `dataType` | Yes | `string`, `number`, `integer`, `boolean`, `date`, `datetime` |
| `description` | No | Prose description for documentation |
| `unit` | No | Physical unit (UCUM notation recommended, e.g. `"Hz"`, `"µm"`, `"s"`) |
| `validation` | No | Rules: `pattern`, `minLength`, `maxLength`, `minimum`, `maximum`, `enum` |

---

## Data Locations

A [data location](../reference/data-locations.md) describes one logical collection of data — its storage paths, folder layout, and how to extract metadata from it.

```json
"dataLocations": [
  {
    "identifier": "two-photon-calcium-imaging",
    "displayName": "Two-Photon Calcium Imaging",
    "description": "Raw two-photon calcium imaging recordings from cortical neurons",
    "dataCategory": "raw",
    "sourceType": "filesystem",
    "tags": ["imaging", "two-photon", "calcium"],
    "customProperties": {
      "microscope": "Bruker",
      "imagingRegion": "cortical layer 2/3"
    },
    "filesystemSource": {
      "rootStoragePaths": [ ... ],
      "entityLayout": [ ... ],
      "metadataMapping": [ ... ]
    }
  }
]
```

### Why is `dataCategory` per data location?

A single dataset often contains multiple categories of data in different locations — for example, raw acquisitions on an instrument PC and motion-corrected results on an analysis server. The `dataCategory` is a property of the location's role in the data lifecycle, not of the dataset as a whole.

This means you can have:

- Two `"raw"` locations (data from two different instruments)
- A `"processed"` location with `"derivedFrom": ["location-a", "location-b"]`
- A `"reference"` location with a brain atlas

See [Data Location Categories](data-location-categories.md) for the full list of category values and when to use each.

### Root Storage Paths

For `filesystem` data locations, `rootStoragePaths` is defined inside `filesystemSource` and can list one path per computing environment.

```json
"filesystemSource": {
  "rootStoragePaths": [
    {
      "identifier": "lab-windows",
      "path": "D:\\Data\\TwoPhoton",
      "storageType": "local",
      "environment": "windows-lab",
      "priority": 1,
      "isAvailable": true
    },
    {
      "identifier": "analysis-mac",
      "path": "/Volumes/DataDrive/TwoPhoton",
      "storageType": "external",
      "environment": "mac-analysis",
      "priority": 1,
      "isAvailable": true
    }
  ],
  "entityLayout": [ ... ]
}
```

Tools select the path whose `environment` matches the current `preferences.environmentIdentifier`. The `priority` field breaks ties when multiple paths match the same environment.

### Provenance with `derivedFrom`

If a data location was produced from other locations, declare this with `derivedFrom`:

```json
{
  "identifier": "processed-calcium-imaging",
  "dataCategory": "processed",
  "sourceType": "filesystem",
  "derivedFrom": ["two-photon-calcium-imaging"],
  "filesystemSource": { ... }
}
```

This is a backwards-looking provenance record. It does not define how the processing was done — that is the responsibility of your pipeline tool (Nextflow, Snakemake, etc.). See [Pipeline Integration](pipeline-integration.md) for how DSM and pipeline tools work together.

---

## Entity Layout

The [entity layout](../reference/entity-layout.md) describes the folder hierarchy within a data location. Each level maps a folder depth to an entity type.

```json
"entityLayout": [
  {
    "name": "subjects",
    "entityType": "subject",
    "matchPattern": "^[A-Za-z0-9]+$",
    "excludePatterns": ["temp", "test", "backup"],
    "isRequired": true,
    "isVariable": true
  },
  {
    "name": "sessions",
    "entityType": "session",
    "matchPattern": "^\\d{8}_[A-Za-z0-9]+$",
    "isRequired": true,
    "isVariable": true
  },
  {
    "name": "recordings",
    "entityType": "recording",
    "matchPattern": "^[A-Za-z0-9_-]+$",
    "isRequired": true,
    "isVariable": true,
    "filePatterns": [ ... ]
  }
]
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Level name (for documentation) |
| `entityType` | Yes | Entity type this level represents |
| `matchPattern` | Conditionally | Regex to match valid folder names; required unless `pathComponentTemplate` is present |
| `excludePatterns` | No | Array of regex patterns — folders matching any are skipped |
| `isRequired` | No | Whether this level must be present |
| `isVariable` | No | `true` = folder names vary per entity; `false` = fixed name |
| `fixedName` | No | The fixed folder name when `isVariable: false` |
| `pathComponentTemplate` | No | Template like `"session-{session_id}"` — used to generate folder names for derived locations |
| `filePatterns` | No | File class definitions at this entity level |

### Handling non-entity levels

If a level does not correspond to a named entity type, use `"entityType": "other"` and give the level a descriptive `name`:

```json
{
  "name": "auxiliary_files",
  "entityType": "other",
  "matchPattern": ".*",
  "isRequired": false,
  "isVariable": false
}
```

---

## File Grouping Patterns

Within an `entityLayout` level, `filePatterns` lists the file grouping patterns expected at that level — one entry per group of files.

```json
"filePatterns": [
  {
    "pattern": ".*\\.tif$",
    "isRequired": true
  },
  {
    "pattern": ".*_metadata\\.json$",
    "isRequired": false
  }
]
```

Each entry has two fields:

| Field | Required | Description |
|-------|----------|-------------|
| `pattern` | Yes | Regex matched against file names at this level |
| `isRequired` | No | Whether a matching file must exist (default `false`) |

If a file matching an `isRequired: true` pattern is absent, tools can report the entity as incomplete.

---

## Metadata Mapping

The [metadata mapping](../reference/metadata-definitions.md#relationship-to-metadatamapping) in a data location declares how to extract each global metadata field from this location's folder/file names.

```json
"metadataMapping": [
  {
    "metadataRef": "subject_id",
    "extraction": {
      "method": "substring",
      "pattern": "0:end",
      "entityLayoutLevel": 0
    }
  },
  {
    "metadataRef": "acquisition_date",
    "extraction": {
      "method": "regex",
      "pattern": "^(\\d{8})_",
      "valueFormat": "yyyyMMdd",
      "entityLayoutLevel": 1
    }
  },
  {
    "metadataRef": "session_id",
    "extraction": {
      "method": "regex",
      "pattern": "^\\d{8}_(.+)$",
      "entityLayoutLevel": 1
    }
  }
]
```

Each entry references a key from `metadataDefinitions` via `metadataRef` and specifies an `extraction` rule:

| Field | Description |
|-------|-------------|
| `method` | `substring`, `regex`, `function`, `template`, `fixed`, `filename`, `filepath` |
| `pattern` | The extraction pattern (substring range, regex, or template string) |
| `entityLayoutLevel` | Zero-based index into `entityLayout` indicating which folder depth to extract from |
| `valueFormat` | Date/time format string, e.g. `"yyyyMMdd"` |

---

## Cross-Location Entity Matching

When a dataset has multiple data locations (e.g. raw and processed), tools need to match entities across them — to find the processed files that correspond to a given raw session. The DSM handles this through `identifierRef` on `entityType`.

```json
"entityTypes": [
  { "name": "session", "identifierRef": "session_id" }
]
```

This declares that two session entities from different locations are the **same session** if:
1. Their extracted `session_id` values are equal, **and**
2. Their parent entities are also matched (hierarchical context is implicit)

You do not need to include parent IDs in `identifierRef` — the entity hierarchy provides the rest of the identity. This design scales to any number of locations: adding a new location that extracts `session_id` is automatically linkable without any further configuration.

If `identifierRef` is absent for an entity type, tools fall back to comparing raw folder names.

---

## Preferences

The [preferences](../reference/preferences.md) block records the context in which the configuration is used:

```json
"preferences": {
  "defaultDataLocationIdentifier": "two-photon-calcium-imaging",
  "environmentIdentifier": "windows-lab"
}
```

`environmentIdentifier` selects which `rootStoragePath` to use; `defaultDataLocationIdentifier` sets which location a tool opens by default. These values represent a specific installation or user session and can be updated without changing the structural description of the dataset.

---

## Best Practices

1. **Define all metadata fields globally** in `metadataDefinitions` — never repeat a field definition in each location. The mapping in each location tells you *how to extract* the field, not what it is.

2. **Use `identifierRef` on every entity type** that appears in more than one data location. This is the only thing needed to enable cross-location entity matching.

3. **Use `derivedFrom`** on every processed or derived location to record its provenance. Pipeline tools can read this to resolve input paths.

4. **Use `filePatterns` with `isRequired: true`** for files that must exist for an entity to be considered complete. This lets tools detect incomplete entities and report missing data.

5. **Use `pathComponentTemplate`** on entity layout levels in derived locations. This lets tools generate output folder names by substituting source entity metadata values, keeping generation and parsing in sync.

6. **Include `description` fields** throughout your configuration. These are the primary surface for LLM tools that read DSM configs — the richer the descriptions, the better LLMs can reason about your data.
