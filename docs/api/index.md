# API Reference

Language-specific libraries for loading and working with Dataset Structure Model configurations programmatically.

<div class="grid cards" markdown>

-   :material-language-python: **Python**

    ---

    The reference reader: validator, directory listings, the dry-run walk, and the conformance runner. `pip install -e .` gives the `dsm` command.

    [:octicons-arrow-right-24: Python API](python.md)

-   :material-language-matlab: **MATLAB**

    ---

    MATLAB `classdef` hierarchy with typed properties, enum classes, and a `fromFile` constructor.

    [:octicons-arrow-right-24: MATLAB API](matlab.md)

</div>

!!! info "Status"
    The Python reader is the reference implementation and passes every [conformance case](../guides/conformance.md). The MATLAB API exists as a first pass on `wip-matlab-api`, written against the pre-freeze draft; it will be rebuilt against the same cases, and `dsm compare` checks its output without a second comparison implementation.
