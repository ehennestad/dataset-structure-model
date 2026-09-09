# Related Work

Almost every mechanism in DSM exists somewhere already. Entities extracted from paths by regular expression, `{token}` templates that build a path from metadata, declarative catalogues of where data lives, attributes read from directory names — all are established practice. What this page sets out is where each of those tools stops, and which combination is left over.

The short version: existing tools do **one direction** (parse or generate, rarely both), for **one layout** (their own), over **one store**, with **no notion that two differently-named things are the same entity**. DSM is the intersection.

---

## The closest neighbours

### PEP / peppy — Portable Encapsulated Projects

A PEP is a YAML config plus a sample table; the `derive` sample modifier turns an attribute into a path via a template:

```yaml
sample_modifiers:
  derive:
    attributes: [read1, read2]
    sources:
      key1: "/path/to/{sample_name}_{sample_type}.bam"
```

This is the same template vocabulary DSM uses for `pathComponentTemplate`, and a PEP sample table *is* an entity table. It is the closest thing conceptually.

The difference is direction. The sample table is authored by the user as a CSV, and `derive` builds paths **from** it; PEP has no filesystem discovery, so it cannot produce the table from a store that already exists. The specification also does not address several storage locations, computing environments, or the same sample appearing in more than one place. PEP is DSM's mirror image: entity table → paths, where DSM is stores → entity table → paths.

### pybids `Entity` / `Config`

pybids indexes a BIDS dataset into a queryable layout. Entities are declared in a JSON config with a name, a regex `pattern` whose first capture group is the value, an optional `directory` pattern, and a `dtype`. That is, mechanically, DSM's `regex` extraction rule, and `bids.json` / `derivatives.json` are a per-layout config file.

What is absent is everything above the extraction: entities are key–value tags attached to a file, not instances with an identity that survives across two differently-named stores, and there are no parent/child relationships between them. The config is also, in practice, BIDS-shaped and Python-only — a config format, not a portable artefact other tools consume.

### NeuroConv `LocalPathExpander`

The closest analogue to DSM's *read* direction, and from the same community. You give it a `base_directory` and an f-string:

```python
"{subject_id}/{session_id}/{session_start_time:%Y-%m-%d}/recording.dat"
```

It matches that against a tree, extracts the values, and returns `source_data` paths plus `metadata`. It supports constraints through Python's format mini-language (`{subject_id:4}` for exactly four characters, `{subject_id:n}` for digits) — genuinely expressive, and more ergonomic than a regex for simple cases.

Two limits. The extracted metadata is a fixed vocabulary — `subject_id`, `session_id`, `session_start_time` — so a dataset whose folder names encode a protocol, a rig or a day number has nowhere to put them; this is exactly the constraint NANSEN's own model has, with four hard-wired variables. And it returns one result per matched path rather than grouping several files under one session. It solves path → metadata for conversion input; it is not a description of a dataset that other tools can read.

### DataJoint

Entity tables for neuroscience, done properly: a schema declares entities and their dependencies, and the `filepath@` external-store type links a record to a file that lives outside the database.

But the direction is the opposite of DSM's. DataJoint is database-first — you design the pipeline, the database holds the entities, and files are attached to rows that already exist. It does not read an existing folder tree and tell you what entities are in it. For a lab whose data is already on disk in a layout nobody designed, DataJoint asks you to define the pipeline that will own it from here on; DSM asks only for a description of what is already there. They are complementary: a DSM reader's entity records are a plausible way to *populate* DataJoint tables.

---

## The wider field

| Tool | Shares with DSM | Where it stops |
|------|-----------------|----------------|
| **BIDS** (and its machine-readable schema) | A formal, machine-readable description of a layout, used to generate validators | Describes exactly *one* layout, prescriptively. DSM's stance is the inverse: describe what exists |
| **Snakemake wildcards / `expand()`** | Path patterns with named wildcards; the same string parses and generates | Per-rule inside a workflow engine; no entity model, no identity, not a shareable artefact |
| **Hive-style partitioning** (Spark, Iceberg, Delta) | Attributes read from directory names, at industrial scale | One fixed convention (`key=value`); yields columns, not entities |
| **Frictionless Data Package** | Portable JSON description of a dataset's files, with validation | Resources and table schemas; nothing derives entities from the layout |
| **Intake, Kedro catalogues** | Declarative YAML mapping names to locations and loaders | Catalogue and loader concerns; no entity hierarchy, no identity |
| **RO-Crate** | Entity descriptions attached to a file collection | Authored JSON-LD metadata about files, not a rule that derives entities from naming |
| **DataLad, DVC** | Managing datasets across places | Versioning and provenance; layout is opaque to them |
| **dtool** | One dataset abstraction over several storage backends | Per-item authored metadata; no layout grammar |
| **openMINDS, NWB, ISA-Tab** | Rich domain and metadata models | Say what a subject *is*, not where its files are or how to find them |
| **DCAT, schema.org `Dataset`** | Portable dataset description | Catalogue-level metadata; no internal structure |

---

## What is left over

Three things we have not found in a single existing artefact:

1. **Identity as a declared, cross-store join key.** The field that makes `2025_05_23/2025_05_23_10_00_00_m110-20250523-001/` and `subject-m110/session-m110-20250523-001/` one row in a session table. Every tool above extracts; none reconciles across stores.

2. **A specified output object, and conformance fixtures as the definition of correct behaviour.** Most of these tools define an input syntax and leave the semantics to whatever the implementation happens to do. DSM defines the [entity record](../reference/entity-record.md) and pins the semantics in [fixtures](conformance.md), which is why two independent readers can be shown to agree.

3. **Descriptive, bidirectional and portable at the same time.** BIDS is portable but prescriptive. Snakemake is bidirectional but not portable. Frictionless is portable but not derivational. PEP is portable and generative, but cannot read a store.

DSM is not novel in any one mechanism. The claim is narrower and, we think, defensible: it is the only description we know of from which a tool in any language can derive entity tables across several stores, and then write back into them.

---

## If you are choosing a tool

- Your data already follows BIDS → use **pybids**. DSM buys you nothing.
- You are designing a pipeline and are willing to let a database own the entities → **DataJoint**.
- You maintain a sample sheet by hand and want file paths built from it → **PEP**.
- You are converting neurophysiology to NWB and your paths encode subject/session/time → **NeuroConv**'s path expander is the shorter road.
- You have several stores, laid out differently, that nobody will reorganise, and you need one entity table over them, from more than one language → that is the case DSM was built for.

---

## Corrections welcome

This survey was compiled from documentation, and tools move. If something here is out of date, or a project we should know about is missing, please open an issue — particularly if it makes one of the three claims above wrong. We would rather adopt an existing standard than maintain a parallel one.

Sources consulted: the [PEP specification](https://pep.databio.org/spec/specification/), [pybids `Entity` documentation](https://bids-standard.github.io/pybids/generated/bids.layout.Entity.html), [NeuroConv path expansion guide](https://neuroconv.readthedocs.io/en/main/user_guide/expand_path.html), and the [DataJoint documentation](https://docs.datajoint.com/) (September 2026).
