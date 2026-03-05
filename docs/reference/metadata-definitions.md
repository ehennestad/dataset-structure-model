# metadataDefinitions

`metadataDefinitions` is a top-level object whose keys are metadata field identifiers. Each value is a metadata definition object. All fields defined here form the shared vocabulary used across all data locations.

```json
"metadataDefinitions": {
  "session_id": {
    "name": "Session ID",
    "ofEntity": "session",
    "dataType": "string",
    "description": "Unique identifier for experimental sessions"
  },
  "imaging_depth": {
    "name": "Imaging Depth",
    "ofEntity": "recording",
    "dataType": "number",
    "unit": "µm",
    "validation": { "minimum": 0, "maximum": 1000 }
  }
}
```

## Metadata definition fields

### `name` *(required)*

| | |
|--|--|
| Type | `string` |

Human-readable name for this field (e.g. `"Session ID"`, `"Imaging Depth"`).

---

### `ofEntity` *(required)*

| | |
|--|--|
| Type | `string` |

The entity type this metadata field belongs to. Must match the `name` of an entry in `entityTypes` (e.g. `"subject"`, `"session"`).

---

### `dataType` *(required)*

| | |
|--|--|
| Type | `string` (enum) |
| Default | `"string"` |

| Value | Description |
|-------|-------------|
| `string` | Text |
| `number` | Floating-point number |
| `integer` | Whole number |
| `date` | Calendar date |
| `time` | Time of day |
| `datetime` | Date and time |
| `boolean` | True/false |
| `array` | List of values |
| `object` | Structured object |

---

### `unit`

| | |
|--|--|
| Type | `string` |
| Example | `"µm"`, `"Hz"`, `"s"`, `"kg"`, `"years"` |

Unit of measurement for numeric fields. Ideally [UCUM](https://ucum.org/)-compatible. For dimensionless quantities, omit this field.

---

### `description`

| | |
|--|--|
| Type | `string` |

Description of what this metadata represents. Used in documentation and by AI agents to understand the field's scientific meaning.

---

### `title`

| | |
|--|--|
| Type | `string` |

User-facing display name for UIs (e.g. `"Subject ID"`, `"Acquisition Date"`). When absent, `name` is used.

---

### `defaultValue`

| | |
|--|--|
| Type | `string`, `number`, `boolean`, or `null` |

Default value when the field cannot be extracted.

---

### `validation`

| | |
|--|--|
| Type | `object` |

Optional validation rules:

| Field | Type | Applies to | Description |
|-------|------|-----------|-------------|
| `pattern` | string (regex) | string | Value must match this pattern |
| `minLength` | integer | string | Minimum character count |
| `maxLength` | integer | string | Maximum character count |
| `minimum` | number | number, integer | Minimum value (inclusive) |
| `maximum` | number | number, integer | Maximum value (inclusive) |
| `enum` | array | any | List of allowed values |

```json
"subject_id": {
  "name": "Subject ID",
  "ofEntity": "subject",
  "dataType": "string",
  "validation": {
    "pattern": "^[A-Za-z0-9]+$",
    "minLength": 3
  }
}
```

---

## Relationship to metadataMapping

`metadataDefinitions` declares *what* a field is. `metadataMapping` on each data location declares *how* to extract it from that location's naming convention. The same field can be extracted differently in each location:

```
metadataDefinitions.session_id
    ↑ metadataRef
    ├── raw-data metadataMapping: regex "^\d{8}_(.+)$" on level 1
    └── processed-data metadataMapping: regex "^session-(.+)$" on level 1
```

Both extract `session_id`; tools can match sessions across locations because they share the same vocabulary.

## Relationship to identifierRef

When an `entityType` declares `"identifierRef": "session_id"`, it means the value extracted for `session_id` is the canonical cross-location identity key for `session` entities. See [Top-Level Structure](overview.md#entitytypes).
