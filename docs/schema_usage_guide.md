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
    }
  },
  "acquisition_date": {
    "name": "Acquisition Date",
    "dataType": "date",
    "description": "Date when data was acquired"
  }
}
```

Each metadata definition includes:
- A unique identifier (the key in the object)
- A human-readable name
- The data type
- An optional description
- Optional validation rules

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
    "metadata": [ ... ],
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
- `metadata`: Metadata fields associated with entities
- `entityRelationships`: Relationships between entity types

### Entity Layout

The `entityLayout` array defines the hierarchical structure of folders and files that make up the data location.

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
- `name`: Name of the level
- `entityType`: Type of entity this level represents
- `matchPattern`: Regular expression for matching valid folders/files
- `excludePatterns`: Patterns for items to exclude
- `isRequired`: Whether this level must exist
- `isVariable`: Whether this level can have variable names
- `filePatterns`: Patterns for matching files at this level

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

The `metadata` array in a data location references global metadata definitions while specifying location-specific extraction rules.

```json
"metadata": [
  {
    "metadataRef": "subject_id",
    "ofEntity": "subject",
    "extraction": {
      "method": "substring",
      "pattern": "0:end"
    }
  },
  {
    "metadataRef": "acquisition_date",
    "ofEntity": "session",
    "extraction": {
      "method": "regex",
      "pattern": "^(\\d{8})_",
      "valueFormat": "yyyyMMdd"
    }
  }
]
```

Each metadata reference includes:
- `metadataRef`: Reference to a global metadata definition
- `ofEntity`: The entity type this metadata belongs to
- `extraction`: Location-specific extraction rules

## Example Configurations

See the `examples/` directory for complete example configurations:

- `neuroscience_dataset_example.json`: Example configuration for neuroscience datasets with two-photon calcium imaging data

## Best Practices

1. **Use Consistent Entity Types**: Use the same entity type names across different data locations when they represent the same concept.

2. **Define Global Metadata**: Define metadata fields globally in `metadataDefinitions` and reference them in data locations, rather than defining them separately in each location.

3. **Use Descriptive Identifiers**: Choose clear, descriptive identifiers for data locations, metadata fields, and other components.

4. **Document Relationships**: Define entity relationships explicitly to capture the semantic structure of your data.

5. **Validate Metadata**: Use validation rules in metadata definitions to ensure data quality.

6. **Use Regular Expressions Carefully**: Write precise regular expressions for `matchPattern` to avoid matching unwanted items.

7. **Include Documentation**: Use the `description` field liberally throughout your configuration to document the purpose of each component.

8. **Consider Multiple Environments**: Define `rootStoragePaths` for all relevant computing environments to ensure portability.
