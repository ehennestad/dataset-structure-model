# MATLAB API

A MATLAB package for loading and working with Dataset Structure Model configurations.
Requires **MATLAB R2021b** or later.

## Installation

Add the `src/matlab` directory to your MATLAB path:

```matlab
addpath('path/to/dataset-structure-model/src/matlab')
```

## Quick start

```matlab
% Load a configuration from a JSON file
model = dsm.DatasetStructureModel.fromFile('examples/neuroscience_dataset_example.json');

% List available data locations
model.listDataLocationIdentifiers()
% ans =
%   1×2 string array
%     "two-photon-calcium-imaging"    "processed-calcium-imaging"

% Get a specific data location
loc = model.getDataLocation('two-photon-calcium-imaging');

% Resolve the storage root path for the current environment
rootPath = loc.resolveRootPath(model.Preferences.EnvironmentIdentifier);

% Traverse entity layout levels
for i = 1:numel(loc.EntityLayout)
    fprintf('%s  (%s)\n', loc.EntityLayout(i).Name, loc.EntityLayout(i).EntityType);
end

% Check whether a folder name matches a level's pattern
sessionLevel = loc.getEntityLayoutLevel('sessions');
sessionLevel.matchesName('20240315_baseline')   % true
sessionLevel.matchesName('temp')                % false (in excludePatterns)

% Get the primary file class at the recording level
recLevel = loc.getEntityLayoutLevel('recordings');
primary  = recLevel.getFileGroupingPattern(dsm.FileRole.primary);
primary.Format   % "image/tiff"

% Look up a metadata definition
md = model.getMetadataDefinition('imaging_depth');
md.Unit     % "µm"
md.DataType % dsm.MetadataDataType.number
```

## Package structure

```
src/matlab/
└── +dsm/
    ├── DatasetStructureModel.m   % top-level class
    ├── DataLocation.m
    ├── EntityType.m
    ├── EntityRelationship.m
    ├── MetadataDefinition.m
    ├── MetadataExtraction.m
    ├── MetadataMappingItem.m
    ├── EntityLayoutLevel.m
    ├── FileGroupingPattern.m
    ├── RootStoragePath.m
    ├── Preferences.m
    ├── DataCategory.m            % enumeration
    ├── StorageType.m             % enumeration
    ├── RelationType.m            % enumeration
    ├── ExtractionMethod.m        % enumeration
    ├── FileRole.m                % enumeration
    ├── FileSystemType.m          % enumeration
    ├── MetadataDataType.m        % enumeration
    └── fromStructArray.m         % package-level helper
```

## Class reference

### `dsm.DatasetStructureModel`

| Method / Property | Description |
|-------------------|-------------|
| `fromFile(filePath)` | Static. Load from a JSON file path. |
| `fromStruct(s)` | Static. Build from a `jsondecode` struct. |
| `SchemaVersion` | string |
| `EntityTypes` | `dsm.EntityType` array |
| `EntityRelationships` | `dsm.EntityRelationship` array |
| `MetadataDefinitions` | `containers.Map` — string key → `dsm.MetadataDefinition` |
| `DataLocations` | `dsm.DataLocation` array |
| `Preferences` | `dsm.Preferences` |
| `getDataLocation(id)` | Return the `DataLocation` with the given identifier. Throws `dsm:DatasetStructureModel:notFound` if not found. |
| `getDefaultDataLocation()` | Shortcut via `Preferences.DefaultDataLocationIdentifier`. |
| `getEntityType(name)` | Return the `EntityType` with the given name. |
| `getMetadataDefinition(key)` | Look up a `MetadataDefinition` by its map key. |
| `listDataLocationIdentifiers()` | Return a `string` array of all data location identifiers. |

### `dsm.DataLocation`

| Method / Property | Description |
|-------------------|-------------|
| `Identifier` | string |
| `DisplayName` | string |
| `DataCategory` | `dsm.DataCategory` |
| `RootStoragePaths` | `dsm.RootStoragePath` array |
| `EntityLayout` | `dsm.EntityLayoutLevel` array (outermost → innermost) |
| `MetadataMapping` | `dsm.MetadataMappingItem` array |
| `DerivedFrom` | string array of source location identifiers |
| `Tags` | string array |
| `CustomProperties` | struct |
| `resolveRootPath(envId)` | Return the path string for the given environment. Selects the matching path with the lowest `Priority` value. Throws `dsm:DataLocation:noPath` if the environment is not found. |
| `getEntityLayoutLevel(nameOrIndex)` | Fetch by name (string) or 0-based index (numeric, matching schema convention). |
| `getMetadataMappingForRef(key)` | Return the `MetadataMappingItem` for the given `metadataRef`, or empty. |

### `dsm.EntityLayoutLevel`

| Method / Property | Description |
|-------------------|-------------|
| `Name` | string |
| `EntityType` | string |
| `MatchPattern` | string (regex) |
| `ExcludePatterns` | string array |
| `FilePatterns` | `dsm.FileGroupingPattern` array |
| `PathComponentTemplate` | string |
| `IsRequired` / `IsVariable` | logical |
| `FixedName` | string (when `IsVariable` is false) |
| `matchesName(name)` | Return `true` if `name` matches `MatchPattern` and none of `ExcludePatterns`. |
| `getFileGroupingPattern(fileType)` | Return `FileGroupingPattern` entries matching the given `dsm.FileRole`. |

### Enumeration classes

Enumeration members are accessible by dot-notation name or by dynamic string:

```matlab
cat = dsm.DataCategory.raw;
cat = dsm.DataCategory.('processed');   % from a string variable
```

| Class | Values |
|-------|--------|
| `dsm.DataCategory` | `raw`, `processed`, `derived`, `imported`, `reference`, `temporary`, `archive`, `custom` |
| `dsm.StorageType` | `local`, `external`, `network`, `cloud`, `removable`, `virtual` |
| `dsm.RelationType` | `oneToOne`, `oneToMany`, `manyToOne`, `manyToMany` |
| `dsm.ExtractionMethod` | `substring`, `regex`, `functionCall`†, `template`, `fixed`, `filename`, `filepath` |
| `dsm.FileRole` | `primary`, `sidecar`, `qc`, `log`, `config`, `auxiliary` |
| `dsm.FileSystemType` | `folder`, `file` |
| `dsm.MetadataDataType` | `string`, `number`, `integer`, `date`, `time`, `datetime`, `boolean`, `array`, `object` |

†`function` is a reserved MATLAB keyword; the member is named `functionCall`. Use `dsm.ExtractionMethod.fromString('function')` to construct from a JSON string value.

## Running the tests

```matlab
addpath('src/matlab')
suite   = matlab.unittest.TestSuite.fromFile('src/matlab/tests/test_load_examples.m');
results = suite.run();
disp(results)
```

## Requirements

- MATLAB R2021b or later (string arrays, `arguments` blocks, `jsondecode` struct arrays)
- No additional toolboxes required
