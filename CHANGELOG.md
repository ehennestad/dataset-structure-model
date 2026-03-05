# Changelog

All notable changes to the Dataset Structure Model schema are documented here.
This project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `identifierRef` and `identifierRefs` on `entityType` — declares the cross-location entity matching key
- `derivedFrom` on `dataLocation` — declares provenance / data lineage between locations
- `tags` and `customProperties` on `dataLocation` — free-form categorisation and tool-specific metadata
- `priority` and `isAvailable` on `rootStoragePath` — path selection and availability hints
- `unit` on metadata definitions — UCUM-compatible unit for numeric fields
- `fileClass` definition (renamed from `fileGroupingPattern`) with `role` enum, `format`, `description`, `groupKey`, and `metadataExtractors`

### Changed
- `fileGroupingPattern` renamed to `fileClass`; `fileType` (free string) replaced by `role` (controlled enum: primary | sidecar | qc | log | config | auxiliary)
- `matchPattern` on `entityLayoutLevel` is now optional when `pathComponentTemplate` is present
- `pathComponentTemplate` description strengthened: tokens reference `metadataDefinitions` keys and serve as generation templates for derived locations
- `additionalProperties: false` added to `entityType`, `preferences`, `entityRelationship`, and `metadataMapping` items for stricter validation

### Fixed
- `entityRelationships` is now correctly defined only at the top level (not inside `dataLocation`)
- `metadataMapping` key name was previously inconsistent in examples

## [1.0.0] - 2025-07-02

### Added
- Initial schema release
- `dataLocations` with `entityLayout`, `metadataMapping`, `rootStoragePaths`
- `entityTypes` and `entityRelationships` at top level
- `metadataDefinitions` with validation rules
- `preferences` with environment and default location selection
- 8 `dataCategory` values: raw, processed, derived, imported, reference, temporary, archive, custom
- 7 `metadataExtraction` methods: substring, regex, function, template, fixed, filename, filepath
- Neuroscience dataset example
- Schema usage guide and data location categories documentation
