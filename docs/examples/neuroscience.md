# Neuroscience Dataset Example

This example models a two-photon calcium imaging dataset with:

- Three entity types: subject → session → recording
- Two data locations: raw acquisitions and motion-corrected processed data
- Multi-environment root storage paths (Windows lab PC + Mac analysis workstation)
- Cross-location entity matching via `identifierRef`
- File classes with `role`, `format`, `groupKey`, and sidecar metadata extractors

Source file: [`examples/neuroscience_dataset_example.json`](https://github.com/ehennestad/dataset-structure-model/blob/main/examples/neuroscience_dataset_example.json)

---

## Entity types and relationships

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
  },
  {
    "name": "recording",
    "description": "An individual imaging recording within a session",
    "identifierRef": "recording_id"
  }
],
"entityRelationships": [
  {
    "sourceEntity": "subject",
    "targetEntity": "session",
    "relationType": "oneToMany",
    "relationName": "hasSessions"
  },
  {
    "sourceEntity": "session",
    "targetEntity": "recording",
    "relationType": "oneToMany",
    "relationName": "hasRecordings"
  }
]
```

The `identifierRef` fields enable cross-location entity matching — any session with the same extracted `session_id` (within the same subject) in both the raw and processed locations is recognised as the same real-world session. No pairwise location declarations are needed.

---

## Metadata definitions

Six metadata fields are defined globally, covering all three entity levels:

| Key | Entity | Type | Notes |
|-----|--------|------|-------|
| `subject_id` | subject | string | Pattern `^[A-Za-z0-9]+$`, min length 3 |
| `acquisition_date` | session | date | Format `yyyyMMdd` |
| `session_id` | session | string | Extracted from folder name after the date |
| `recording_id` | recording | string | Full folder name |
| `imaging_depth` | recording | number | Unit: µm; range 0–1000 |
| `frame_rate` | recording | number | Unit: Hz |

`imaging_depth` and `frame_rate` are extracted from the sidecar metadata JSON file, not from folder names, via a `metadataExtractors` function.

---

## Raw data location

**Folder structure:**

```
D:\Data\TwoPhoton\
└── m110/                          ← subject (matches ^[A-Za-z0-9]+$)
    └── 20240315_baseline/         ← session (matches ^\d{8}_[A-Za-z0-9]+$)
        └── run-001/               ← recording (matches ^[A-Za-z0-9_-]+$)
            ├── 20240315_m110_baseline_run001.tif       (primary)
            └── 20240315_m110_baseline_run001_metadata.json  (sidecar)
```

**Root storage paths** — two environments:

```json
"rootStoragePaths": [
  {
    "identifier": "lab-windows-path",
    "path": "D:\\Data\\TwoPhoton",
    "storageType": "local",
    "environment": "windows-lab",
    "priority": 1
  },
  {
    "identifier": "analysis-mac-path",
    "path": "/Volumes/DataDrive/TwoPhoton",
    "storageType": "external",
    "environment": "mac-analysis",
    "priority": 1
  }
]
```

Tools select the path whose `environment` matches `preferences.environmentIdentifier`.

**File classes at the recording level:**

```json
"filePatterns": [
  {
    "pattern": ".*\\.tif$",
    "role": "primary",
    "format": "image/tiff",
    "description": "Raw calcium imaging frames, 16-bit single-channel",
    "isRequired": true,
    "groupKey": "imaging-data"
  },
  {
    "pattern": ".*_metadata\\.json$",
    "role": "sidecar",
    "format": "application/json",
    "description": "Acquisition parameters: frame rate, imaging depth, laser power, PMT settings",
    "isRequired": false,
    "groupKey": "imaging-data",
    "metadataExtractors": [
      { "method": "function", "extractorFunction": "extractImagingParameters" }
    ]
  }
]
```

Both files share `groupKey: "imaging-data"` — they are expected to co-occur. If the `.tif` is present without its sidecar JSON, tools can report the recording as incomplete.

**Metadata mapping** — extracted from folder names:

| Field | Level | Method | Pattern |
|-------|-------|--------|---------|
| `subject_id` | 0 (subject) | `substring` | `0:end` (entire folder name) |
| `acquisition_date` | 1 (session) | `regex` | `^(\d{8})_` — first 8 digits |
| `session_id` | 1 (session) | `regex` | `^\d{8}_(.+)$` — part after date |
| `recording_id` | 2 (recording) | `substring` | `0:end` |

---

## Processed data location

The processed location stores motion-corrected outputs on the lab Windows PC only:

```
D:\Data\Processed\TwoPhoton\
└── m110/
    └── 20240315_baseline/
        └── processed/            ← fixed folder name
            ├── *_motion_corrected.tif
            ├── *_roi_masks.mat    (auxiliary)
            └── *_calcium_traces.mat  (auxiliary)
```

Key differences from the raw location:

- `"derivedFrom": ["two-photon-calcium-imaging"]` — links back to the source.
- The third layout level has `"isVariable": false` and `"fixedName": "processed"` — all sessions use the same subfolder name.
- The `recording_id` metadata mapping is absent because the `processed` folder does not vary per recording.

---

## Preferences

```json
"preferences": {
  "defaultDataLocationIdentifier": "two-photon-calcium-imaging",
  "environmentIdentifier": "windows-lab"
}
```

These values reflect a specific user session on the lab Windows PC. Update `environmentIdentifier` when working from the Mac analysis machine.
