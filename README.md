# Dataset Structure Model

[![CI](https://github.com/ehennestad/dataset-structure-model/actions/workflows/ci.yml/badge.svg)](https://github.com/ehennestad/dataset-structure-model/actions/workflows/ci.yml)

## Summary

**What it is.** The Dataset Structure Model is a JSON Schema (draft-07) for describing how a scientific dataset is laid out: where its files live, what entity hierarchy the folder structure encodes (for example study → site → participant → visit), and how metadata can be read out of file paths and names.

**How it works.** A dataset is described declaratively in a single JSON document. The document specifies one or more storage locations, the entity layout under each location, how directories and filenames map to entity identifiers and metadata fields, how files are grouped by role (primary data, sidecars, QC, logs, configuration), and how entities at different locations refer to the same underlying thing. Tooling reads this description and can then validate paths, look up files, extract metadata, and treat heterogeneous datasets through a uniform interface — without bespoke filesystem code for each dataset.

**Why it exists.** Scientific datasets are organised in many different ways, and that variation is the main barrier to writing reusable analysis pipelines and data-management tools. Existing standards such as BIDS, NWB, and openMINDS define specific data formats or domain models; none of them describe arbitrary dataset layouts in a portable, machine-readable way. The Dataset Structure Model fills that gap, so the same tooling can work across datasets, storage backends, and computing environments.

## Repository Contents

- **schema/**: `DatasetStructureModel.schema.json` (the config) and `EntityRecord.schema.json` (what readers emit)
- **docs/**: Documentation (mkdocs site)
- **examples/**: Example configurations
- **conformance/**: Fixtures a reader must pass — a config, a directory listing and the entity records to produce
- **src/python/dsm/**: The Python reference reader and `dsm` command (validate, listing, walk, compare, conformance)
- **src/matlab/+dsm/**: The MATLAB reader (`addpath src/matlab`), passing the same conformance cases
- **tests/**: Schema, example, cross-reference and docs-snippet tests (`pytest tests/`)

## Key Features

- **Standardized Dataset Description**: Define the structure of scientific datasets in a consistent, machine-readable format
- **Physical and Semantic Mapping**: Capture both the physical layout on disk and the semantic organization of data
- **Metadata Extraction**: Define rules for extracting metadata from folder and file names, with one contract across languages
- **File Grouping**: Describe which files belong to an entity, including folders where many entities' files are mixed together
- **Defined Output**: Readers emit entity records — the same object from MATLAB or Python — and conformance fixtures check that they do
- **Cross-environment Support**: Handle datasets distributed across multiple storage locations and computing environments
- **Entity Relationships**: Define semantic relationships between different types of entities in your data
- **Validation**: Ensure metadata values conform to expected formats and constraints

## Getting Started

```bash
pip install -e .
dsm validate examples/flat_session_files.json
dsm walk conformance/flat-session-files/config.json conformance/flat-session-files/listing.json
```

```matlab
addpath("src/matlab")
config = dsm.loadConfig("conformance/flat-session-files/config.json");
result = dsm.walk(config, dsm.loadListing("conformance/flat-session-files/listing.json"));
disp(dsm.renderReport(config, result))
```

1. Read the [Quick Start](docs/getting-started/quickstart.md) and [Core Concepts](docs/getting-started/concepts.md)
2. Work through the [Usage Guide](docs/guides/usage-guide.md)
3. Look at the [example configurations](examples/) — a flat folder of session files, raw and processed two-photon data, a toy dataset
4. See the [Schema Reference](docs/reference/index.md); [Metadata Extraction](docs/reference/metadata-extraction.md) and [Entity Record](docs/reference/entity-record.md) are the parts readers implement

## Example Use Cases

### Neuroscience Research Data

The model can organize two-photon imaging data with:
- Subjects as the top level
- Sessions within each subject
- Raw and processed data folders
- Metadata extraction for subject IDs, session dates, and experiment details

### Clinical Trial Data

The model can manage clinical trial data with:
- Study as the top level
- Sites within each study
- Patients within each site
- Visits within each patient
- Different data types (imaging, lab results, questionnaires) at the lowest level

### Multi-environment Data Processing

The model supports data processing workflows where:
- Raw data is collected on lab computers
- Processing happens on high-performance computing clusters
- Analysis occurs on researchers' personal workstations
- Each environment has different paths to the same logical data

## Schema Evolution

The Dataset Structure Model uses semantic versioning. The current version is **1.0.0**, the frozen core: the `filesystem` source type, the extraction methods `substring`, `regex`, `template`, `fixed` and `function`, declared entity identity, file-level entities and the entity record. Blocks marked DRAFT in the schema (`spreadsheet`, `database`, `api` sources; `sidecar` extraction) may change without a major version bump. See [CHANGELOG.md](CHANGELOG.md).

## Contributing

Contributions to improve the model are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
