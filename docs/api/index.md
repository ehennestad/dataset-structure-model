# API Reference

Language-specific libraries for loading and working with Dataset Structure Model configurations programmatically.

<div class="grid cards" markdown>

-   :material-language-python: **Python**

    ---

    Pydantic v2 models, configuration loader, JSON Schema validator, and entity traversal utilities.

    [:octicons-arrow-right-24: Python API](python.md)

-   :material-language-matlab: **MATLAB**

    ---

    MATLAB `classdef` hierarchy with typed properties, enum classes, and a `fromFile` constructor.

    [:octicons-arrow-right-24: MATLAB API](matlab.md)

</div>

!!! info "Status"
    Neither API is released. Both exist as first passes on `wip-*` branches written against the pre-freeze draft and will be brought to 1.0.0 against a shared set of conformance fixtures (directory listings plus the [entity records](../reference/entity-record.md) a reader must produce), so that the MATLAB and Python readers are checked against the same expectations.
