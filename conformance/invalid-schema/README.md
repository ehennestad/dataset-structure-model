# invalid-schema

A config that fails JSON Schema validation (a removed property, a `substring` pattern that is not a slice). A reader must refuse it with error code `schema-validation` before looking at any listing.
