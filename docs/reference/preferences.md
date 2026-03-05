# preferences

`preferences` is a required top-level object that provides runtime context. It answers two questions: which computing environment is currently active, and which data location should be used when none is explicitly specified.

`additionalProperties` is `false`.

## Fields

### `environmentIdentifier` *(required)*

| | |
|--|--|
| Type | `string` |
| Example | `"windows-lab"`, `"mac-analysis"`, `"hpc-cluster"` |

Identifies the current computing environment. Tools use this to select the correct `rootStoragePath` from each data location's `rootStoragePaths` array — choosing the entry whose `environment` field matches this value.

This field is the bridge between the multi-environment path declarations in `rootStoragePaths` and the single active environment at runtime. Change this value when moving the same config to a different machine.

---

### `defaultDataLocationIdentifier` *(required)*

| | |
|--|--|
| Type | `string` |

The `identifier` of the data location to use when a tool does not specify which location to operate on. Must match the `identifier` of one of the entries in `dataLocations`.

---

## Example

```json
"preferences": {
  "defaultDataLocationIdentifier": "two-photon-calcium-imaging",
  "environmentIdentifier": "windows-lab"
}
```

With this config, a tool that asks "give me the root path for the default location" will look up `two-photon-calcium-imaging`, find its `rootStoragePaths`, and select the entry with `"environment": "windows-lab"`.

---

## Design note

`preferences` represents instance-level state (the active environment for a specific installation or user session) rather than the dataset's structure itself. It is included in the config file rather than a separate settings file to keep DSM configs self-contained: a single JSON file is sufficient to fully describe both the dataset and the context in which it should be interpreted.
