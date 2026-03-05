# Data Location Categories

The `dataCategory` property on a [`dataLocation`](../reference/data-locations.md) specifies the role of that data in the research workflow or data lifecycle. It helps tools understand how to handle different types of data appropriately.

`dataCategory` is a property of each individual location, not of the dataset as a whole — a single dataset commonly has several locations with different categories. See [Usage Guide → Why is `dataCategory` per data location?](usage-guide.md#why-is-datacategory-per-data-location) for the rationale.

---

## Summary

| Category | Role | Typical access |
|----------|------|---------------|
| `raw` | Original data from instruments | Read-only |
| `processed` | Cleaned/prepared for analysis | Read-mostly |
| `derived` | Results of analysis | Read/write |
| `imported` | Data from external sources | Read-only |
| `reference` | Calibration or annotation data | Read-only |
| `temporary` | Intermediate processing artefacts | Deletable |
| `archive` | Historical, not actively used | Read-only, cold storage |
| `custom` | Specialised, project-specific | Varies |

---

## `raw`

Original, unprocessed data directly from acquisition devices or instruments.

**Characteristics:**

- Unaltered from its original state
- Often considered the "ground truth" for the experiment
- Should be protected from modification
- May contain noise, artefacts, or other imperfections

**Examples:**

- Raw microscopy images from a two-photon microscope
- Unprocessed electrophysiology recordings
- Behavioural tracking videos as captured
- Direct output from scientific instruments

---

## `processed`

Data that has undergone initial processing steps to clean, format, or prepare it for analysis.

**Characteristics:**

- Derived from raw data through standardised processing pipelines
- Processing steps are typically reproducible
- More suitable for direct analysis than raw data
- May include corrections for known artefacts

**Examples:**

- Motion-corrected calcium imaging data
- Filtered electrophysiology signals
- Preprocessed MRI scans
- Normalised gene expression data

Use `derivedFrom` to link a processed location back to its source raw location.

---

## `derived`

Data that results from analysis of raw or processed data, representing higher-level information.

**Characteristics:**

- Created through analytical procedures or computational models
- Represents extracted features, patterns, or results
- Often more abstract than the data it was derived from
- May combine information from multiple sources

**Examples:**

- Extracted neural activity traces
- Identified cell locations or ROIs
- Statistical analysis results
- Fitted model parameters

Use `derivedFrom` to link a derived location back to its processed or raw inputs.

---

## `imported`

Data that originated from an external source and has been incorporated into the current dataset.

**Characteristics:**

- Not generated within the current research workflow
- May follow different conventions or formats
- Often needs transformation to integrate with local data
- Provenance information is particularly important

**Examples:**

- Public datasets incorporated into analysis
- Data shared by collaborators
- Reference data from published studies
- Data imported from another laboratory

---

## `reference`

Standard or canonical data used for comparison, calibration, or annotation.

**Characteristics:**

- Serves as a benchmark or standard
- Typically stable and well-documented
- Often used across multiple experiments or analyses
- May include standardised annotations or classifications

**Examples:**

- Brain atlases
- Standard gene annotations
- Calibration datasets
- Reference spectra or waveforms

---

## `temporary`

Intermediate data that is not intended for long-term storage.

**Characteristics:**

- Created during processing or analysis workflows
- Not essential for reproducing final results
- Often large in volume but low in long-term value
- May be automatically deleted after a pipeline run

**Examples:**

- Intermediate processing steps
- Cache files
- Partial results during batch processing
- Debug outputs

---

## `archive`

Data that is preserved for historical reference but is no longer actively used.

**Characteristics:**

- No longer needed for active analysis
- Preserved for compliance, reference, or potential future use
- Often stored on lower-cost, slower-access storage
- May be compressed or in specialised archival formats

**Examples:**

- Completed project data
- Data from published studies
- Historical datasets
- Backup copies of important data

---

## `custom`

Data that does not fit the standard categories and has a specialised role.

**Characteristics:**

- Serves a purpose specific to a particular research workflow
- May combine aspects of multiple standard categories
- Requires custom handling or processing
- Needs additional documentation to clarify its role

**Examples:**

- Specialised simulation outputs
- Custom visualisation data
- Hybrid data products
- Project-specific data types

Use the `description` field and `tags` on the data location to document what `"custom"` means in your context.

---

## Usage guidelines

- Consider the role of the data in your research workflow, not just its format.
- Use `raw` even if the files are large — it is about role, not size.
- Use `processed` or `derived` (not both) for a single processing step; `processed` for cleaning/preparation, `derived` for analysis outputs that change the form of the data.
- Always set `derivedFrom` when the category is `processed` or `derived` so that provenance is traceable.
- Use `reference` for any data that multiple experiments share as a stable baseline.
- Mark locations as `archive` rather than deleting them — the DSM entry preserves the record of what the data was.
