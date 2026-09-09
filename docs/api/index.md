# API Reference

Language-specific libraries for loading and working with Dataset Structure Model configurations programmatically.

<div class="grid cards" markdown>

-   :material-language-python: **Python**

    ---

    The reference reader: validator, directory listings, the dry-run walk, and the conformance runner. `pip install -e .` gives the `dsm` command.

    [:octicons-arrow-right-24: Python API](python.md)

-   :material-language-matlab: **MATLAB**

    ---

    The `+dsm` package: `loadConfig`, listings, `walk`, `compareResults`, `renderReport`, and the conformance runner. `addpath src/matlab`.

    [:octicons-arrow-right-24: MATLAB API](matlab.md)

</div>

!!! info "Status"
    Both readers pass every [conformance case](../guides/conformance.md). The Python reader is the reference; the MATLAB reader's records are additionally checked with the Python comparator (`dsm compare`), so the two are known to agree on the interchange format. Neither is released on a package index yet.
