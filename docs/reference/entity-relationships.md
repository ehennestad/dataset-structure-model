# entityRelationships

`entityRelationships` is an optional top-level array that declares semantic relationships between entity types. Relationships are independent of physical storage — the same relationship holds regardless of which data location is being queried.

`additionalProperties` is `false` on `entityRelationship`.

## Fields

### `sourceEntity` *(required)*

| | |
|--|--|
| Type | `string` |

Name of the source entity type. Must match a `name` in `entityTypes`.

---

### `targetEntity` *(required)*

| | |
|--|--|
| Type | `string` |

Name of the target entity type. Must match a `name` in `entityTypes`.

---

### `relationType` *(required)*

| | |
|--|--|
| Type | `string` (enum) |

Cardinality of the relationship from `sourceEntity` to `targetEntity`:

| Value | Meaning |
|-------|---------|
| `oneToOne` | Each source entity has exactly one target entity |
| `oneToMany` | Each source entity has zero or more target entities |
| `manyToOne` | Many source entities share one target entity |
| `manyToMany` | Many source entities relate to many target entities |

---

### `relationName`

| | |
|--|--|
| Type | `string` |
| Example | `"hasSessions"`, `"belongsTo"`, `"contains"` |

Optional semantic label for this relationship. Used in documentation and graph representations.

---

### `isRequired`

| | |
|--|--|
| Type | `boolean` |
| Default | `true` |

When `true`, every `sourceEntity` instance must have at least one related `targetEntity` instance for the dataset to be considered complete.

---

### `description`

| | |
|--|--|
| Type | `string` |

Human-readable explanation of what this relationship means scientifically.

---

## Example

```json
"entityRelationships": [
  {
    "sourceEntity": "subject",
    "targetEntity": "session",
    "relationType": "oneToMany",
    "relationName": "hasSessions",
    "description": "Each subject participates in multiple recording sessions over time"
  },
  {
    "sourceEntity": "session",
    "targetEntity": "recording",
    "relationType": "oneToMany",
    "relationName": "hasRecordings",
    "isRequired": false,
    "description": "A session may contain one or more individual recordings"
  }
]
```

---

## Design note

Entity relationships describe the *semantic* structure of the data. The *physical* containment (subject folders contain session folders) is described by `entityLayout`. These are intentionally separate: the same semantic relationship (e.g. subject → session) holds across all data locations regardless of how the physical hierarchy is arranged.
