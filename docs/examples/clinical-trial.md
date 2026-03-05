# Clinical Trial Dataset Example

This example models a multi-site longitudinal clinical trial dataset with:

- Four entity types: site → participant → visit → assessment
- A `manyToMany` relationship (participant transfers between sites)
- Three data locations: raw clinical data, imported normative reference data, and derived analysis results
- `derivedFrom` linking the analysis results to both of its inputs
- `pathComponentTemplate` on the derived location for output path generation
- NIfTI + sidecar JSON `groupKey` co-occurrence constraint
- `identifierRefs` on site and participant for composite cross-location matching

Source file: [`examples/clinical_trial_example.json`](https://github.com/ehennestad/dataset-structure-model/blob/main/examples/clinical_trial_example.json)

---

## Entity types and relationships

```json
"entityTypes": [
  { "name": "site",        "isPrimary": false, "identifierRef": "site_id" },
  { "name": "participant", "isPrimary": true,  "identifierRef": "participant_id" },
  { "name": "visit",       "identifierRef": "visit_id" },
  { "name": "assessment",  "identifierRef": "assessment_id" }
]
```

The `isPrimary: true` on `participant` marks participants as the top-level unit of interest — tools that build entity tables will use this as the primary index.

**Relationships:**

```json
"entityRelationships": [
  { "sourceEntity": "site",        "targetEntity": "participant", "relationType": "oneToMany",  "relationName": "enrolls" },
  { "sourceEntity": "participant", "targetEntity": "visit",       "relationType": "oneToMany",  "relationName": "hasVisits" },
  { "sourceEntity": "visit",       "targetEntity": "assessment",  "relationType": "oneToMany",  "relationName": "includes" },
  { "sourceEntity": "site",        "targetEntity": "participant", "relationType": "manyToMany", "relationName": "transferredTo" }
]
```

The `manyToMany` relationship models that participants may transfer between sites during the trial — a common occurrence in real clinical studies. The same pair of entity types can have more than one relationship with different `relationName` values.

---

## Metadata definitions

Seven fields are defined globally:

| Key | Entity | Type | Notes |
|-----|--------|------|-------|
| `site_id` | site | string | Pattern `^SITE\d{3}$` |
| `participant_id` | participant | string | Pattern `^P\d{3}$` |
| `visit_id` | visit | string | E.g. `V01`, `V12` |
| `visit_date` | visit | date | |
| `assessment_id` | assessment | string | E.g. `MRI-T1`, `MMSE` |
| `arm` | participant | string | Enum: `treatment`, `placebo`, `control` |
| `age_at_baseline` | participant | integer | Unit: years; range 18–100 |

`arm` uses a controlled vocabulary via the `enum` validation rule. `age_at_baseline` has a physical unit and a range constraint.

---

## Raw clinical data location

**Folder structure:**

```
/mnt/trial-data/raw/
└── SITE001/                          ← site
    └── P001/                         ← participant
        └── V01/                      ← visit
            └── MRI-T1/               ← assessment
                ├── sub-P001_T1w.nii.gz     (primary, groupKey: nifti-pair)
                ├── sub-P001_T1w.json        (sidecar, groupKey: nifti-pair)
                ├── MMSE_scores.csv          (primary)
                └── MRI-T1_report.pdf        (qc)
```

**File classes at the assessment level:**

| Pattern | Role | Format | `groupKey` |
|---------|------|--------|-----------|
| `.*\.nii\.gz$` | `primary` | `application/x-nifti` | `nifti-pair` |
| `.*\.json$` | `sidecar` | `application/json` | `nifti-pair` |
| `.*_scores\.csv$` | `primary` | `text/csv` | — |
| `.*_report\.pdf$` | `qc` | `application/pdf` | — |

The NIfTI and JSON sidecar share `groupKey: "nifti-pair"` — they are expected to be present together. If one is missing, tools report the assessment as incomplete.

Note that some assessments (e.g. blood draw) will have no NIfTI file at all — `isRequired: false` on both NIfTI entries means this is valid.

**Multi-environment paths:**

```json
"rootStoragePaths": [
  {
    "identifier": "server-path",
    "path": "/mnt/trial-data/raw",
    "storageType": "network",
    "environment": "analysis-server"
  },
  {
    "identifier": "local-path",
    "path": "C:\\TrialData\\Raw",
    "storageType": "local",
    "environment": "windows-site-workstation"
  }
]
```

---

## Imported normative reference data

```json
{
  "identifier": "reference-normative-data",
  "dataCategory": "imported",
  "customProperties": {
    "source": "published",
    "accessMode": "read-only"
  }
}
```

This location holds external normative datasets (healthy population cognitive norms, age-matched imaging atlases) that were not produced by this trial. Using `"dataCategory": "imported"` — rather than `"raw"` — signals that the data originates from outside the current research workflow and provenance information is particularly important.

`customProperties` is used here for free-form tool-specific metadata (source provenance, access mode). This is not part of the DSM's semantic model — it is for tool-specific extensions.

---

## Derived analysis results

```json
{
  "identifier": "derived-analysis-results",
  "dataCategory": "derived",
  "derivedFrom": ["clinical-raw-data", "reference-normative-data"]
}
```

`derivedFrom` lists both inputs: the raw clinical measurements and the normative reference data. This is the lineage record — the analysis pipeline reads both sources and writes outputs here.

**Folder structure** (two-level, skipping the site level):

```
/mnt/trial-data/derived/
└── P001/
    └── V01/
        ├── P001_V01_derived_scores.csv      (primary)
        ├── P001_V01_imaging_features.csv     (primary)
        └── P001_V01_analysis_log.txt         (log)
```

Note that this location does not have a site level — the analysis is at the participant/visit level. This is intentional: not every data location needs to mirror every entity level of the raw data.

**`pathComponentTemplate` for output generation:**

```json
"entityLayout": [
  {
    "name": "participants",
    "entityType": "participant",
    "pathComponentTemplate": "{participant_id}",
    "matchPattern": "^P\\d{3}$",
    "isVariable": true
  },
  {
    "name": "visits",
    "entityType": "visit",
    "pathComponentTemplate": "{visit_id}",
    "matchPattern": "^V\\d{2}$",
    "isVariable": true
  }
]
```

A pipeline writing outputs for participant `P001`, visit `V01` substitutes the metadata values into the templates to get the output path: `/mnt/trial-data/derived/P001/V01/`.

---

## What this example demonstrates

- **Four-level hierarchy** — DSM handles any depth; each level maps to a named entity type.
- **`manyToMany` relationship** — participant transfers between sites are modelled explicitly without complicating the folder structure.
- **Multiple `derivedFrom` inputs** — analysis results can depend on more than one source location.
- **Shallow derived location** — derived data does not need to mirror the full hierarchy of its source.
- **`pathComponentTemplate`** — enables pipeline tools to generate output paths from source entity metadata without hardcoding paths.
- **`imported` category** — distinguishes externally sourced reference data from data produced in this study.
- **`customProperties`** — free-form tool-specific metadata that the DSM schema does not constrain.
