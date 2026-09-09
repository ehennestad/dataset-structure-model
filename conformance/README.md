# Conformance fixtures

One directory per case. Each holds a `config.json` (a DSM config), a `listing.json` (a directory snapshot, see `schema/DirectoryListing.schema.json`), an `expected.json` (the entity records a reader must produce, or the error it must raise) and a `README.md` saying what the case checks.

A reader passes a case when, given the config and the listing, it produces exactly the expected records and unmatched entries, or raises the expected error. Comparison rules, the listing format and the expectation format are specified in `docs/guides/conformance.md`.

The repository's own test suite checks that every case is self-consistent (`tests/test_conformance.py`): the config validates, every expected path exists in the listing, every listing entry is accounted for, and every declarative extraction and file pattern in the expectation re-evaluates to the same result.
