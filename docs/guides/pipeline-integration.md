# Pipeline Integration

The Dataset Structure Model is a **data contract**, not a pipeline definition. It describes where data lives and how it is organised — pipeline tools (Nextflow, Snakemake, etc.) are responsible for defining how data is processed.

This page explains how the two work together.

---

## The separation of concerns

| Responsibility | Tool |
|---------------|------|
| Where is the data? | DSM (`rootStoragePaths`) |
| How is it organised? | DSM (`entityLayout`, `metadataMapping`) |
| What are the entities? | DSM (`entityTypes`, `entityRelationships`) |
| How was it produced? | DSM (`derivedFrom`) |
| What processing steps ran? | Pipeline tool (Nextflow, Snakemake, …) |
| What parameters were used? | Pipeline tool |

A pipeline reads the DSM config to discover input paths. It writes outputs to a location declared in the DSM as `"dataCategory": "processed"` or `"derived"`. The DSM records the lineage; the pipeline handles the execution.

---

## Declaring derived locations

A processed or derived data location should always set `derivedFrom`:

```json
{
  "identifier": "motion-corrected",
  "displayName": "Motion-Corrected Imaging",
  "dataCategory": "processed",
  "derivedFrom": ["two-photon-raw"],
  "rootStoragePaths": [
    {
      "identifier": "analysis-server",
      "path": "/data/processed/motion-corrected",
      "storageType": "local",
      "environment": "linux-server"
    }
  ],
  "entityLayout": [
    {
      "name": "subjects",
      "entityType": "subject",
      "pathComponentTemplate": "{subject_id}",
      "matchPattern": "^[A-Za-z0-9]+$",
      "isVariable": true
    },
    {
      "name": "sessions",
      "entityType": "session",
      "pathComponentTemplate": "{session_id}",
      "matchPattern": "^[A-Za-z0-9_-]+$",
      "isVariable": true
    }
  ],
  ...
}
```

`derivedFrom` is a backwards-looking provenance record. It tells anyone reading the config "this data was produced from the listed source locations". It does not specify the processing algorithm or parameters.

---

## Resolving input paths at pipeline runtime

A pipeline tool can read the DSM config to resolve the input path for a given entity:

1. Read `derivedFrom` on the derived location to find the source location identifier.
2. Look up the source location in `dataLocations`.
3. Select the `rootStoragePath` whose `environment` matches the current environment.
4. Walk the source `entityLayout` to construct the path for the entity being processed.

This means you do not hardcode paths in your pipeline scripts. The DSM config is the single source of truth.

---

## Generating output paths with `pathComponentTemplate`

For derived data locations, declare `pathComponentTemplate` on each entity layout level. This allows tools to construct output folder names by substituting source entity metadata values:

```json
{
  "name": "sessions",
  "entityType": "session",
  "pathComponentTemplate": "session-{session_id}",
  "matchPattern": "^session-[A-Za-z0-9_-]+$",
  "isVariable": true
}
```

Generation flow (pipeline writes output):

1. Get `session_id` from the source entity (via `derivedFrom` + `identifierRef`).
2. Substitute into the template: `session-{session_id}` → `session-m110-001`.
3. Create the output folder at `{rootPath}/subject-m110/session-m110-001/`.

Parse flow (reading back with tools):

- `matchPattern` and `metadataMapping` work normally to extract metadata from the folder names.

When `pathComponentTemplate` is present, `matchPattern` is optional (tools can auto-derive it from the template), but it is good practice to include both so the naming convention is explicit.

---

## Cross-location entity matching

After a pipeline run, tools need to connect processed outputs back to their source entities. This is handled by `identifierRef` on each `entityType`:

```json
"entityTypes": [
  { "name": "session", "identifierRef": "session_id" }
]
```

Any two session entities from different locations that share the same extracted `session_id` value (and whose parent subject entities also match) are treated as the same real-world session. No additional configuration is needed.

---

## Example integration pattern

**Nextflow pipeline reading a DSM config:**

```groovy
// Read the DSM config
def dsm = new groovy.json.JsonSlurper().parse(file(params.dsm_config))

// Find the raw location
def rawLocation = dsm.dataLocations.find { it.identifier == "two-photon-raw" }

// Select the root path for the current environment
def rootPath = rawLocation.rootStoragePaths
    .find { it.environment == params.environment }
    .path

// Emit one work item per session
Channel.fromPath("${rootPath}/*/*")
    .map { sessionDir -> [sessionDir.parent.name, sessionDir.name, sessionDir] }
    .set { sessions_ch }
```

The pipeline does not hardcode `/data/raw` — it reads it from the DSM config. If the data moves (or is accessed from a different environment), only the DSM config needs updating.

---

## Updating the DSM after a pipeline run

A pipeline may optionally update the DSM config after completing a run:

- Set `"isAvailable": true` on newly populated root storage paths.
- Update `"schemaVersion"` if the structure changed.

This is optional. The DSM config is a description of the dataset structure, not a runtime state file. Do not store pipeline execution state (job IDs, completion timestamps, error logs) in the DSM — use your pipeline tool's native mechanisms for that.
