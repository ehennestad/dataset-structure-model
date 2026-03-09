# Schema Design Decisions

This document captures the rationale behind key design choices in the Dataset Structure Model. It is intended for contributors and tool builders who need to understand the *why* behind the schema, not just the *what*.

---

## The DSM is descriptive, not prescriptive

Most existing data standards (BIDS, ISA, NWB) require you to conform your data to a specified structure. The DSM takes the opposite approach: you describe your data as it actually exists on disk. This is a deliberate choice to support the large volume of heterogeneous, legacy, and instrument-specific datasets that do not conform to any standard and are unlikely to be reorganised.

The implication is that the DSM is a *recipe*, not a *schema for the data itself*. It tells tools how to read your data; it does not tell you how to organise it.

---

## `dataCategory` is per data location, not global

Each `dataLocation` has its own `dataCategory` (raw, processed, derived, etc.). This is intentional: a single dataset often contains multiple categories of data stored in different locations with different folder structures and naming conventions. The category is a property of a location's role in the data lifecycle, not of the dataset as a whole.

---

## `metadataDefinitions` is global; `metadataMapping` is per location

Metadata fields (e.g., `session_id`, `subject_id`) are defined once globally in `metadataDefinitions`. Each `dataLocation` then declares, in `metadataMapping`, how to *extract* those fields from its specific folder or file naming convention.

This separation ensures that:

1. Metadata field names are consistent across locations (no aliasing)
2. The same field can be extracted differently in each location (different regex, different level)
3. Cross-location entity matching (via `identifierRef`) operates on a shared vocabulary

---

## Cross-location entity identity is declared on `entityType`, not on location pairs

To match entities across data locations (e.g., the same session in raw and processed data), the `identifierRef` field on `entityType` declares which metadata field serves as the canonical identity key. This applies globally to all locations — any two locations that both extract the same value for `session_id` for a `session` entity are considered to refer to the same session.

This design was chosen over pairwise `sourceLocation`/`targetLocation` declarations because:

- It scales to N locations without O(N²) declarations
- Adding a new location that extracts `session_id` is automatically linkable
- The identity key is a property of what the entity *is*, not of any particular pair of locations

The hierarchical context is implicit: a session is identified by (its own `identifierRef` value AND its parent subject's `identifierRef` value). Tools traverse the entity hierarchy when matching.

---

## `pathComponentTemplate` serves double duty: documentation and path generation

`pathComponentTemplate` on `entityLayoutLevel` (e.g., `"session-{session_id}"`) serves two purposes:

1. **Documentation**: makes the naming convention human-readable at a glance
2. **Generation**: for derived data locations, tools substitute source entity metadata values into the template to construct new output folder names

When `pathComponentTemplate` is present, `matchPattern` becomes optional. Tools can auto-derive a matching regex from the template. This avoids the two declarations getting out of sync.

---

## `derivedFrom` is for provenance, not pipeline definition

`derivedFrom` on a `dataLocation` declares which source locations were the input to produce this location's data. It is a backwards-looking record of lineage — it does not define how the processing was done (that is the responsibility of pipeline tools such as Nextflow or Snakemake).

The intended integration pattern is: pipeline tools read DSM configs to resolve input paths, write outputs to the declared derived location, and optionally update `derivedFrom` after a run.

---

## `fileGroupingPattern` describes which files belong to an entity

`filePatterns` on an `entityLayoutLevel` lists the regex patterns for files expected at that level, with an `isRequired` flag to mark files whose absence indicates an incomplete entity. The schema deliberately keeps this simple — pattern matching and completeness checking — without prescribing file roles, formats, or co-occurrence groups. Domain-specific semantics can be captured in `description` fields elsewhere in the config.

---

## No dataset-level metadata in the schema

The DSM deliberately excludes dataset-level descriptive metadata (name, creator, DOI, domain, license). This information belongs in existing standards: BIDS `dataset_description.json`, NWB file-level attributes, openMINDS, schema.org Dataset, or DCAT. The DSM focuses exclusively on structural metadata — how data is organised, how entities relate, and how metadata can be extracted from paths.

Encouraging the use of existing standards for descriptive metadata avoids duplication and ensures interoperability with data catalogs and repositories that already consume those standards.

---

## `preferences` is instance-level, not schema-level

The `preferences` block (default data location, current environment) represents the state of a specific installation or user session. It is part of the config file rather than a separate file to keep the DSM self-contained: a single JSON file describes both the dataset structure and the context in which it should be interpreted.
