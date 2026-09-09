# Python API

!!! warning "Status: models generated from the pre-freeze draft on branch `wip-python-api`"
    Not released. `src/python/models.py` was generated with datamodel-codegen from the pre-freeze draft schema and predates `filesystemSource`, `access`, structural levels and the 1.0.0 extraction contract. The plan is a small validator and dry-run tool first — schema validation, the cross-reference rules, and a walk over a directory listing that reports entities found, unmatched files, duplicate identities and unresolved extractors — then regenerated models.

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
