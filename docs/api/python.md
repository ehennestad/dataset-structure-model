# Python API

!!! warning "Coming soon"
    The Python package is under development. This page will be updated when the first release is available.

The Python API provides:

- **Pydantic v2 models** — typed Python objects for every schema definition
- **Configuration loader** — `load(source)` accepting a file path, URL, or dict
- **JSON Schema validator** — validates a config against the bundled schema
- **Traversal utilities** — `get_data_location`, `resolve_root_path`, `iter_entity_levels`

## Planned installation

```bash
pip install dataset-structure-model
```

## Planned usage

```python
from dataset_structure_model import load

# Load from a file
dsm = load("my-dataset.json")

# Access entity types
for entity_type in dsm.entity_types:
    print(entity_type.name, entity_type.identifier_ref)

# Resolve a data location's root path for the current environment
location = dsm.get_data_location("raw-data")
root_path = location.resolve_root_path(environment="linux-server")

# Iterate entity layout levels
for level in location.entity_layout:
    print(level.name, level.entity_type, level.match_pattern)
```

## Source code

The source is in [`src/python/`](https://github.com/ehennestad/dataset-structure-model/tree/main/src/python) of the repository.
