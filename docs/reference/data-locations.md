# dataLocations

`dataLocations` is a required array of data location objects. Each entry describes one logical collection of data — typically corresponding to one category of data (raw, processed, derived, etc.).

`additionalProperties` is `false` on the `dataLocation` object.

## Required fields

### `identifier`

| | |
|--|--|
| Type | `string` |
| Example | `"two-photon-calcium-imaging"` |

Unique identifier for this data location within the config. Used in cross-references: `derivedFrom`, `preferences.defaultDataLocationIdentifier`.

---

### `displayName`

| | |
|--|--|
| Type | `string` |
| Example | `"Two-Photon Calcium Imaging"` |

Human-readable name shown in UIs and reports.

---

### `dataCategory`

| | |
|--|--|
| Type | `string` (enum) |
| Default | `"raw"` |

The role of this location in the data lifecycle. See [Data Location Categories](../guides/data-location-categories.md) for full definitions.

| Value | Meaning |
|-------|---------|
| `raw` | Original unprocessed data from instruments |
| `processed` | Cleaned or reformatted data |
| `derived` | Analysis results and extracted features |
| `imported` | Data from external sources |
| `reference` | Standard or normative comparison data |
| `temporary` | Intermediate processing outputs |
| `archive` | Historical or completed project data |
| `custom` | Project-specific category |

---

### `sourceType`

| | |
|--|--|
| Type | `string` (enum) |
| Values | `"filesystem"` \| `"spreadsheet"` \| `"database"` \| `"api"` |

The type of data source this location represents. Determines which source-specific block is required:

| Value | Required block |
|-------|---------------|
| `filesystem` | `filesystemSource` |
| `spreadsheet` | `spreadsheetSource` + `entityType` |
| `database` | `databaseSource` + `entityType` |
| `api` | `apiSource` + `entityType` |

---

## Optional fields

### `filesystemSource`

| | |
|--|--|
| Type | `object` |
| Required when | `sourceType` is `"filesystem"` |

Contains all filesystem-specific configuration. Fields:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `rootStoragePaths` | Yes | array | Storage root paths, one per environment. See below. |
| `entityLayout` | Yes | array of `entityLayoutLevel` | Physical hierarchy mapping folders/files to entities. See [entityLayout reference](entity-layout.md). |
| `metadataMapping` | No | array | Extraction rules for global metadata fields. |
| `pathTemplate` | No | string | Informational path template (e.g. `"{rootPath}/{subject}/{session}"`). |
| `additionalFolders` | No | array of string | Folder names at the leaf level that are not entity hierarchy members. |

**`rootStoragePaths`** — each entry:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `identifier` | Yes | string | Unique ID for this path entry |
| `path` | Yes | string | Absolute file system path |
| `environment` | No | string | Environment identifier this path is for (matches `preferences.environmentIdentifier`) |
| `storageType` | No | enum | `local` \| `external` \| `network` \| `cloud` \| `removable` \| `virtual` |
| `volumeName` | No | string | Disk/volume name (useful for removable media) |
| `priority` | No | integer | Selection order when multiple paths match the active environment (lower = preferred, default 1) |
| `isAvailable` | No | boolean | Runtime availability hint (default `true`) |

---

## Optional fields

### `description`

| | |
|--|--|
| Type | `string` |

Detailed description of this data location's purpose, contents, or provenance.

---

### `derivedFrom`

| | |
|--|--|
| Type | `array` of `string` (location identifiers) |
| Example | `["two-photon-calcium-imaging"]` |

Declares the source data locations that were used to produce this location's data. Enables:

1. **Provenance**: tools can trace the data lineage graph
2. **Path generation**: tools know which source entities to draw metadata from when constructing derived output paths using `pathComponentTemplate`

```json
{
  "identifier": "processed-data",
  "dataCategory": "processed",
  "derivedFrom": ["raw-data"],
  ...
}
```

---

### `tags`

| | |
|--|--|
| Type | `array` of `string` |
| Example | `["imaging", "two-photon", "raw-data"]` |

Free-form tags for categorisation, filtering, or search.

---

### `customProperties`

| | |
|--|--|
| Type | `object` (any JSON values) |

Free-form key-value pairs for domain-specific or tool-specific metadata not covered by the schema. Values can be any JSON type.

```json
"customProperties": {
  "microscope": "Bruker",
  "imagingRegion": "cortical layer 2/3"
}
```
