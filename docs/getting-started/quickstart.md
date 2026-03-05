# Quick Start

This guide walks you through creating a minimal valid DSM config and validating it.

## Prerequisites

- A text editor
- Python 3.8+ with `jsonschema` installed (for validation):

```bash
pip install jsonschema
```

## Step 1: Download the schema

```bash
curl -O https://raw.githubusercontent.com/ehennestad/dataset-structure-model/main/schema/DatasetStructureModel.schema.json
```

Or clone the repository:

```bash
git clone https://github.com/ehennestad/dataset-structure-model.git
```

## Step 2: Create a minimal config

Create a file `my-dataset.json`:

```json
{
  "schemaVersion": "1.0.0",
  "entityTypes": [
    { "name": "subject", "identifierRef": "subject_id" },
    { "name": "session", "identifierRef": "session_id" }
  ],
  "metadataDefinitions": {
    "subject_id": {
      "name": "Subject ID",
      "ofEntity": "subject",
      "dataType": "string"
    },
    "session_id": {
      "name": "Session ID",
      "ofEntity": "session",
      "dataType": "string"
    }
  },
  "dataLocations": [
    {
      "identifier": "raw-data",
      "displayName": "Raw Data",
      "dataCategory": "raw",
      "rootStoragePaths": [
        {
          "identifier": "my-machine",
          "path": "/data/raw",
          "environment": "my-machine"
        }
      ],
      "entityLayout": [
        {
          "name": "subjects",
          "entityType": "subject",
          "matchPattern": "^[A-Za-z0-9]+$"
        },
        {
          "name": "sessions",
          "entityType": "session",
          "matchPattern": "^\\d{8}_.*$"
        }
      ],
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
          "metadataRef": "session_id",
          "extraction": {
            "method": "regex",
            "pattern": "^\\d{8}_(.+)$",
            "entityLayoutLevel": 1
          }
        }
      ]
    }
  ],
  "preferences": {
    "defaultDataLocationIdentifier": "raw-data",
    "environmentIdentifier": "my-machine"
  }
}
```

This config describes a dataset with two hierarchy levels:

```
/data/raw/
├── m110/              ← subject folder (matched by subject matchPattern)
│   ├── 20250523_session1/   ← session folder (matched by session matchPattern)
│   └── 20250601_session2/
└── m220/
    └── 20250524_session1/
```

## Step 3: Validate

```bash
python -m jsonschema -i my-dataset.json schema/DatasetStructureModel.schema.json
```

No output means the config is valid. Any errors will describe exactly what is wrong and where.

## Step 4: Add more detail

From here you can:

- Add a second data location for processed data with [`derivedFrom`](../reference/data-locations.md#derivedfrom)
- Describe the files inside each entity folder using [`filePatterns`](../reference/entity-layout.md#filepatterns)
- Declare entity relationships in [`entityRelationships`](../reference/entity-relationships.md)
- Add environment-specific paths for your lab workstation and analysis server

See the [Neuroscience Dataset example](../examples/neuroscience.md) for a complete real-world config, or the [Usage Guide](../guides/usage-guide.md) for detailed walkthroughs of each feature.
