# Top-Level Structure

A DSM config is a JSON object. `additionalProperties` is `false` — no keys outside this list are permitted.

## Required properties

### `schemaVersion`

| | |
|--|--|
| Type | `string` |
| Pattern | `^\d+\.\d+\.\d+$` |
| Example | `"1.0.0"` |

The version of the DSM schema this config conforms to, using [semantic versioning](https://semver.org/). Consumers use this to determine compatibility.

---

### `dataLocations`

| | |
|--|--|
| Type | `array` of [`dataLocation`](data-locations.md) |
| Min items | 1 |

The core of the config. Each item describes one folder tree — its category, root paths, entity hierarchy, and metadata extraction rules. See [dataLocations reference](data-locations.md).

---

### `preferences`

| | |
|--|--|
| Type | `object` |

Runtime context: which environment is active and which data location to use by default. See [preferences reference](preferences.md).

---

## Optional properties

### `entityTypes`

| | |
|--|--|
| Type | `array` of entity type objects |

Declares the semantic entity types present in this dataset. Each item has:

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `name` | Yes | string | Entity type name (e.g. `"subject"`, `"session"`) |
| `description` | No | string | What this entity represents |
| `identifierRef` | No | string | Key in `metadataDefinitions` that uniquely identifies this entity across locations |
| `identifierRefs` | No | array of strings | Composite identity key (use instead of `identifierRef` when multiple fields are needed) |
| `isPrimary` | No | boolean | Whether this is the primary entity type |
| `color` | No | string | UI hint color (e.g. `"#FF0000"`) |

The `identifierRef` field is the cross-location entity matching key. See [Core Concepts](../getting-started/concepts.md#cross-location-entity-matching) for details.

---

### `entityRelationships`

| | |
|--|--|
| Type | `array` of [`entityRelationship`](entity-relationships.md) |

Semantic relationships between entity types, independent of physical storage. See [entityRelationships reference](entity-relationships.md).

---

### `metadataDefinitions`

| | |
|--|--|
| Type | `object` (string keys → metadata definition objects) |

Global dictionary of metadata fields. Keys are used as references in `metadataMapping` and `identifierRef`. See [metadataDefinitions reference](metadata-definitions.md).
