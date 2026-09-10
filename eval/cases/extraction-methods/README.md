# extraction-methods

Listing from `conformance/extraction-methods`. Repurposed: as a reader fixture it exists to exercise every extraction method, which makes most of it unsuitable for grading a writer.

Graded: the `data/` level is structural (no `entityType`, absent from `parents`), `sub-CD02/raw/` does not match it, `sub-XY/` does not match the subject level, and date and time come out of a `2025-05-23T100000_s7` component as ISO values.

**Not graded.** The reference config's `rig: "2p-rig-1"` (`fixed`) and `experiment: "unknown"` (`defaultValue`) are facts no listing contains — a skill inventing them would be wrong, so nothing here requires them. Its `template` and `normalize` rules are likewise method-coverage, not inference.
