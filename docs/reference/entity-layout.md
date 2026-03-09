# entityLayout

`entityLayout` is an ordered array on each `dataLocation`. Each item defines one level of the folder hierarchy, from outermost (index 0) to innermost. Together they declare how physical folder structure maps to semantic entities.

`additionalProperties` is `false` on `entityLayoutLevel`.

## Required fields

### `name`

| | |
|--|--|
| Type | `string` |
| Example | `"subjects"`, `"sessions"` |

Label for this hierarchy level. Used in documentation, UI, and error messages.

---

### `entityType`

| | |
|--|--|
| Type | `string` |
| Example | `"subject"`, `"session"`, `"recording"` |

The semantic entity type that folders (or files) at this level represent. Should match the `name` of an entry in `entityTypes`.

---

## Optional fields

### `matchPattern`

| | |
|--|--|
| Type | `string` (regex) |
| Example | `"^[A-Za-z0-9]+$"`, `"^\\d{8}_.*$"` |

Regular expression matched against folder or file names at this level. Only entries whose names match are considered valid entities; non-matching names are silently skipped.

Required for non-derived data locations. Optional when `pathComponentTemplate` is present — tools can derive a regex from the template automatically.

---

### `pathComponentTemplate`

| | |
|--|--|
| Type | `string` |
| Example | `"{subject_id}"`, `"session-{session_id}"`, `"{subject_id}_{acquisition_date}"` |

Template declaring how this level's name is composed from metadata fields. Tokens in curly braces reference keys in `metadataDefinitions`.

Serves two purposes:

1. **Documentation** — makes the naming convention immediately readable
2. **Path generation** — for derived locations, tools substitute source entity metadata values to construct new output folder names

```json
{
  "name": "sessions",
  "entityType": "session",
  "pathComponentTemplate": "session-{session_id}",
  "matchPattern": "^session-[A-Za-z0-9-]+$"
}
```

Generation flow: source entity has `session_id = "m110-001"` → template produces `session-m110-001/`.

---

### `fileSystemType`

| | |
|--|--|
| Type | `string` (enum) |
| Values | `"folder"` (default), `"file"` |

Whether entities at this level are represented by folders or individual files.

---

### `filePatterns`

| | |
|--|--|
| Type | `array` of `fileGroupingPattern` objects |

Describes the file grouping patterns expected at this level. Each entry:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `pattern` | Yes | string (regex) | Matched against file names at this level |
| `isRequired` | No | boolean | Whether a matching file must exist for the entity to be complete (default `false`) |

```json
"filePatterns": [
  { "pattern": ".*\\.dat$",       "isRequired": true  },
  { "pattern": ".*\\.dat\\.meta$","isRequired": true  },
  { "pattern": ".*\\.log$",       "isRequired": false }
]
```

---

### `excludePatterns`

| | |
|--|--|
| Type | `array` of `string` |
| Default | `[]` |
| Example | `["temp", "backup", "^\\..*"]` |

Patterns for folder or file names to exclude at this level. Applied before `matchPattern`.

---

### `isRequired`

| | |
|--|--|
| Type | `boolean` |
| Default | `true` |

Whether this level must exist in the hierarchy. When `false`, the level is optional and its absence does not constitute a structural error.

---

### `isVariable`

| | |
|--|--|
| Type | `boolean` |
| Default | `true` |

Whether entities at this level have variable names (`true`, the common case) or a single fixed name (`false`). Use `false` for structural folders like `processed/` or `raw/` that are always the same.

---

### `fixedName`

| | |
|--|--|
| Type | `string` |
| Example | `"processed"` |

The fixed folder name when `isVariable` is `false`.
