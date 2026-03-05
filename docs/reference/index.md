# Schema Reference

Complete reference for every property in the Dataset Structure Model schema (version 1.0.0).

The schema file is at [`schema/DatasetStructureModel.schema.json`](https://github.com/ehennestad/dataset-structure-model/blob/main/schema/DatasetStructureModel.schema.json).

## Top-level structure

| Property | Required | Type | Description |
|----------|----------|------|-------------|
| `schemaVersion` | Yes | string (semver) | Schema version, e.g. `"1.0.0"` |
| `dataLocations` | Yes | array | One or more data location definitions |
| `preferences` | Yes | object | Active environment and default location |
| `entityTypes` | No | array | Semantic entity type declarations |
| `entityRelationships` | No | array | Relationships between entity types |
| `metadataDefinitions` | No | object | Global metadata field dictionary |

## Reference pages

- [Top-Level Structure](overview.md)
- [dataLocations](data-locations.md)
- [entityLayout](entity-layout.md)
- [metadataDefinitions](metadata-definitions.md)
- [entityRelationships](entity-relationships.md)
- [preferences](preferences.md)
