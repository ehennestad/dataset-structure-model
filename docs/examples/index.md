# Examples

Complete, annotated Dataset Structure Model configurations for real-world dataset types.

<div class="grid cards" markdown>

-   :material-microscope: **Neuroscience Dataset**

    ---

    Two-photon calcium imaging with raw and processed data locations, multi-environment paths, and cross-location entity matching.

    [:octicons-arrow-right-24: Read the walkthrough](neuroscience.md)

-   :material-hospital-box: **Clinical Trial Dataset**

    ---

    Four-level hierarchy (site → participant → visit → assessment) with imported demographic data, derived analysis results, and composite entity matching.

    [:octicons-arrow-right-24: Read the walkthrough](clinical-trial.md)

</div>

---

The JSON source files for all examples are in the [`examples/`](https://github.com/ehennestad/dataset-structure-model/tree/main/examples) directory of the repository and can be validated against the schema:

```bash
python -m jsonschema -i examples/neuroscience_dataset_example.json schema/DatasetStructureModel.schema.json
python -m jsonschema -i examples/clinical_trial_example.json schema/DatasetStructureModel.schema.json
```
