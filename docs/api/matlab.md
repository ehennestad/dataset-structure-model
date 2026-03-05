# MATLAB API

!!! warning "Coming soon"
    The MATLAB package is under development. This page will be updated when the first release is available.

The MATLAB API provides:

- **`classdef` hierarchy** — typed MATLAB objects for every schema definition, with a `fromStruct` constructor
- **Enum classes** — `DataCategory`, `StorageType`, `Method`, `RelationType` as MATLAB enumerations
- **Top-level class** — `DatasetStructureModel.fromFile(path)` to load a config from a JSON file
- **Traversal methods** — `getDataLocation`, `resolveRootPath`

## Planned usage

```matlab
% Add the package to the path
addpath('path/to/dataset-structure-model/src/matlab')

% Load a configuration
dsm = DatasetStructureModel.DatasetStructureModel.fromFile('my-dataset.json');

% Access entity types
for i = 1:numel(dsm.EntityTypes)
    fprintf('%s — identifierRef: %s\n', dsm.EntityTypes(i).Name, dsm.EntityTypes(i).IdentifierRef);
end

% Get a data location
location = dsm.getDataLocation('raw-data');

% Resolve root path for the current environment
rootPath = location.resolveRootPath('linux-server');
```

## Requirements

- MATLAB R2021b or later (string array support)
- Optionally: Python with `jsonschema` installed for full JSON Schema validation

## Source code

The source is in [`src/matlab/`](https://github.com/ehennestad/dataset-structure-model/tree/main/src/matlab) of the repository.
