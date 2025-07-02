# Dataset Structure Model: Usage Guide

This guide explains how to use the Dataset Structure Model schema to describe scientific datasets, with a focus on the key features that enable standardized representation of heterogeneous datasets.

## Table of Contents

1. [Introduction](#introduction)
2. [Schema Overview](#schema-overview)
3. [Key Components](#key-components)
   - [Schema Version](#schema-version)
   - [Metadata Definitions](#metadata-definitions)
   - [Data Locations](#data-locations)
   - [Entity Layout](#entity-layout)
   - [Entity Relationships](#entity-relationships)
   - [Metadata References](#metadata-references)
4. [Example Configurations](#example-configurations)
5. [Best Practices](#best-practices)

## Introduction

The Dataset Structure Model provides a standardized way to describe the structure of scientific datasets, capturing both their physical layout on disk and their semantic organization. It enables tools and pipelines to understand and operate on datasets regardless of how the data is actually laid out on disk.

## Schema Overview

A Dataset Structure Model configuration is a JSON document that conforms to the `DatasetStructureModel.schema.json` schema. The configuration consists of several main sections:

```json
{
  "schemaVersion": "1.0.0",
  "metadataDefinitions": { ... },
  "dataLocations": [ ... ],
  "preferences": { ... }
}
```

## Key Components

### Schema Version

The `schemaVersion` property specifies the version of the schema that the configuration follows. This helps tools determine compatibility.

```json
"schemaVersion": "1.0.0"
```

### Metadata Definitions

The `metadataDefinitions` section defines metadata fields that can be referenced across multiple data locations. This ensures consistent metadata definitions while allowing for location-specific extraction methods.

```json
"metadataDefinitions": {
  "subject_id": {
    "name": "Subject ID",
    "dataType": "string",
    "description": "Unique identifier for research subjects",
    "validation": {
      "pattern": "^[A-Za-z0-9]+$",
      "minLength": 3
    },
    "ofEntity": "subject"
  },
  "acquisition_date": {
    "name": "Acquisition Date",
    "dataType": "date",
    "description": "Date when data was acquired",
    "ofEntity": "session"
  }
}
```

Each metadata definition includes:
- A unique identifier (the key in the object)
- A human-readable name
- The data type
- An optional description
- Optional validation rules
- `ofEntity`: The entity type this metadata is associated with

### Data Locations

The `dataLocations` array contains definitions for different types of data, each with its own organization structure.

```json
"dataLocations": [
  {
    "identifier": "two-photon-calcium-imaging",
    "displayName": "Two-Photon Calcium Imaging",
    "description": "Raw two-photon calcium imaging recordings",
    "dataCategory": "raw",
    "rootStoragePaths": [ ... ],
    "pathTemplate": "{rootPath}/{subject}/{session}/{recording}",
    "entityLayout": [ ... ],
    "metadataMapping": [ ... ],
    "entityRelationships": [ ... ],
    "tags": ["imaging", "two-photon", "calcium"]
  }
]
```

Key properties of a data location:
- `identifier`: Unique identifier for the data location
- `displayName`: Human-readable name
- `dataCategory`: Category defining its role in the data lifecycle
- `rootStoragePaths`: Physical storage locations
- `pathTemplate`: Template showing the expected structure
- `entityLayout`: Definition of the folder/file structure
- `metadataMapping`: Extraction rules for metadata fields associated with entities (see below)
- `entityRelationships`: Relationships between entity types

#### FAQ: Why is `dataCategory` a property of each `dataLocation`?

**Q:** *Why does each `dataLocation` have a `dataCategory`? Shouldn’t the category be global, or belong to the data itself?*

**A:**  
The `dataCategory` property is defined on each `dataLocation` because a single dataset often contains multiple types of data, each with a different role in the research lifecycle. For example, you might have:

- Two separate locations for raw (acquired) data—perhaps from different acquisition systems or stored on different drives.
- A third location containing processed or derived data, generated after running analysis pipelines.

Each of these storage locations is described as a separate `dataLocation` in the model, and the `dataCategory` (e.g., `"raw"`, `"processed"`, `"derived"`) signals the role that the data in that location plays. This design supports:

- **Multiple locations with the same category:** You can have several `dataLocations` with `dataCategory: "raw"` if you acquire raw data on different systems.
- **Clear mapping of role to storage:** The `dataCategory` tells tools and users how to handle data from that particular location (e.g., raw data might be read-only, processed data might be subject to updates).
- **Flexible, explicit data lifecycle tracking:** It’s possible to describe a complete flow of data from raw acquisition through processing to derived results, with each step stored in a different place.

This approach allows the schema to clearly represent real-world scenarios where data is split across multiple locations, and the *role* of the data is determined by its location and context—not just by its content.

**Example:**
- After an experiment, you might have:
    - Raw data from System A on External Drive A (`dataLocation` 1, `dataCategory: "raw"`)
    - Raw data from System B on External Drive B (`dataLocation` 2, `dataCategory: "raw"`)
    - Processed data in a Dropbox folder (`dataLocation` 3, `dataCategory: "processed"`)
  All three refer to the same experimental entities (subjects, sessions), but are tracked separately.

For details about the available categories and their recommended usage, see [Data Location Categories](data_location_categories.md).

### Entity Layout

The `entityLayout` array defines the hierarchical structure of folders and files that make up the data location. **Each level should specify an `entityType`, which describes the semantic type of entity (such as `subject`, `session`, or `recording`) that the folder or file at that level represents.** 

```json
"entityLayout": [
  {
    "name": "subjects",
    "entityType": "subject",
    "matchPattern": "^[A-Za-z0-9]+$",
    "excludePatterns": ["temp", "test"],
    "isRequired": true,
    "isVariable": true
  },
  {
    "name": "sessions",
    "entityType": "session",
    "matchPattern": "^\\d{8}_[A-Za-z0-9]+$",
    "excludePatterns": [],
    "isRequired": true,
    "isVariable": true
  }
]
```

Each level in the entity layout includes:
- `name`: Name of the level (for documentation/readability)
- `entityType`: **Semantic type of entity this level represents (e.g., 'subject', 'session', 'recording').** This field is required and is used for mapping between the folder structure and the dataset's semantic organization.
- `matchPattern`: Regular expression for matching valid folders/files at this level
- `excludePatterns`: Patterns for items to exclude
- `isRequired`: Whether this level must exist
- `isVariable`: Whether this level can have variable names (vs. a fixed name)
- `filePatterns`: Patterns for matching files at this level

#### Handling ambiguous or miscellaneous levels

If a level does not correspond to a clearly defined entity, or represents miscellaneous content, **you may use `"other"` as the `entityType`**.  
When using `"other"`, make sure the `name` field at that level clearly indicates its purpose (for example: `"auxiliary_files"`, `"unstructured"`, or `"legacy_data"`). This ensures each `"other"` is uniquely identified and understandable, even if multiple `"other"` levels exist in a dataset.

```json
"entityLayout": [
  {
    "name": "auxiliary_files",
    "entityType": "other",
    "matchPattern": ".*",
    "isRequired": false,
    "isVariable": false
  }
]
```

> **Note:** The `entityType` field allows tools to construct data tables (such as subject or session tables) from arbitrary folder structures, by relating physical structure to semantic entities.

### Entity Relationships

The `entityRelationships` array defines semantic relationships between entity types, independent of their physical layout.

```json
"entityRelationships": [
  {
    "sourceEntity": "subject",
    "targetEntity": "session",
    "relationType": "oneToMany",
    "relationName": "hasSessions",
    "description": "A subject can have multiple recording sessions"
  },
  {
    "sourceEntity": "session",
    "targetEntity": "recording",
    "relationType": "oneToMany",
    "relationName": "hasRecordings",
    "description": "A session can have multiple recordings"
  }
]
```

Each relationship includes:
- `sourceEntity`: The source entity type
- `targetEntity`: The target entity type
- `relationType`: The cardinality of the relationship
- `relationName`: Optional name for the relationship
- `description`: Human-readable description

### Metadata References

The `metadataMapping` array in a data location references global metadata definitions while specifying location-specific extraction rules.

```json
"metadataMapping": [
  {
    "metadataRef": "subject_id",
    "extraction": {
      "method": "substring",
      "pattern": "0:end"
    }
  },
  {
    "metadataRef": "acquisition_date",
    "extraction": {
      "method": "regex",
      "pattern": "^(\\d{8})_",
      "valueFormat": "yyyyMMdd"
    }
  }
]
```

Each metadata mapping includes:
- `metadataRef`: Reference to a global metadata definition in `metadataDefinitions`
- `extraction`: Location-specific extraction rules for this metadata field

> **Note:** The `ofEntity` property is defined globally in the `metadataDefinitions` block, not repeated in `metadataMapping`.

## Example Configurations

See the `examples/` directory for complete example configurations:

- `neuroscience_dataset_example.json`: Example configuration for neuroscience datasets with two-photon calcium imaging data

## Best Practices

1. **Use Consistent Entity Types**: Use the same entity type names across different data locations when they represent the same concept. The `entityType` field in `entityLayout` is central to mapping physical structure to semantic meaning.
2. **Define Global Metadata**: Define metadata fields globally in `metadataDefinitions` and reference them in data locations, rather than defining them separately in each location.
3. **Use Descriptive Identifiers**: Choose clear, descriptive identifiers for data locations, metadata fields, and other components.
4. **Document Relationships**: Define entity relationships explicitly to capture the semantic structure of your data.
5. **Validate Metadata**: Use validation rules in metadata definitions to ensure data quality.
6. **Use Regular Expressions Carefully**: Write precise regular expressions for `matchPattern` to avoid matching unwanted items.
7. **Include Documentation**: Use the `description` field liberally throughout your configuration to document the purpose of each component.
8. **Consider Multiple Environments**: Define `rootStoragePaths` for all relevant computing environments to ensure portability.
