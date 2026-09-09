# invalid-reference

A config that passes JSON Schema validation but fails the cross-reference rules (dangling `identifierRef`, unknown level name in an extraction rule, unknown `derivedFrom` target). A reader must refuse it with error code `reference-integrity` and produce no records.
