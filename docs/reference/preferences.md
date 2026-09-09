# preferences

`preferences` is an optional top-level object holding runtime context: which computing environment is active and which data location to use when none is specified.

`additionalProperties` is `false`.

## Fields

### `environmentIdentifier`

| | |
|--|--|
| Type | `string` |
| Example | `"windows-lab"`, `"mac-analysis"`, `"hpc-cluster"` |

Selects, in every data location, the `rootStoragePath` whose `environment` matches. Not needed when the config is used on one environment and its root paths carry no `environment`.

### `defaultDataLocationIdentifier`

| | |
|--|--|
| Type | `string` |

The location a tool operates on when not told otherwise. Must be a `dataLocations` identifier.

## The local overlay

These values describe a machine or a user session, not the dataset, and they change from checkout to checkout. Keeping them only in a shared, version-controlled config makes every machine fight over the same line. So:

- `preferences` may be omitted from the shared config.
- A reader that finds a file named **`<config basename>.local.json`** next to the config takes `preferences` from it in preference to the shared one. The overlay is a JSON object with a `preferences` key and nothing else, and it is meant to be git-ignored.

```json
{
  "preferences": {
    "defaultDataLocationIdentifier": "processed",
    "environmentIdentifier": "mac-analysis"
  }
}
```

Whether a root path is currently reachable is runtime state as well; readers report it, the config does not store it.
