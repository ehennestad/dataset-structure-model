# Data Location Categories

The `category` property in a data location definition specifies the role of the data in the research workflow or data lifecycle. This helps tools understand how to handle different types of data appropriately. Below are detailed descriptions of each category:

## Raw

**Description**: Original, unprocessed data directly from acquisition devices or instruments.

**Characteristics**:
- Unaltered from its original state
- Often considered the "ground truth" for the experiment
- Should be preserved and protected from modification
- May contain noise, artifacts, or other imperfections

**Examples**:
- Raw microscopy images from a two-photon microscope
- Unprocessed electrophysiology recordings
- Original behavioral tracking videos
- Direct output from scientific instruments

## Processed

**Description**: Data that has undergone initial processing steps to clean, format, or prepare it for analysis.

**Characteristics**:
- Derived from raw data through standardized processing pipelines
- Processing steps are typically reversible or reproducible
- Often more suitable for direct analysis than raw data
- May include corrections for known artifacts or experimental issues

**Examples**:
- Motion-corrected calcium imaging data
- Filtered electrophysiology signals
- Preprocessed MRI scans
- Normalized gene expression data

## Derived

**Description**: Data that results from analysis of raw or processed data, representing higher-level information.

**Characteristics**:
- Created through analytical procedures or computational models
- Represents extracted features, patterns, or results
- Often more abstract than the data it was derived from
- May combine information from multiple sources

**Examples**:
- Extracted neural activity traces
- Identified cell locations or ROIs
- Statistical analysis results
- Fitted model parameters

## Imported

**Description**: Data that originated from external sources and has been incorporated into the current dataset.

**Characteristics**:
- Not generated within the current research workflow
- May follow different conventions or formats
- Often needs to be transformed to integrate with local data
- Provenance information is particularly important

**Examples**:
- Public datasets incorporated into analysis
- Data shared by collaborators
- Reference data from published studies
- Data imported from other laboratories

## Reference

**Description**: Standard or canonical data used for comparison, calibration, or annotation.

**Characteristics**:
- Serves as a benchmark or standard
- Typically stable and well-documented
- Often used across multiple experiments or analyses
- May include standardized annotations or classifications

**Examples**:
- Brain atlases
- Standard gene annotations
- Calibration datasets
- Reference spectra or waveforms

## Temporary

**Description**: Intermediate data that is not intended for long-term storage.

**Characteristics**:
- Created during processing or analysis workflows
- Not essential for reproducing final results
- Often large in volume but low in long-term value
- May be automatically deleted after a certain period

**Examples**:
- Intermediate processing steps
- Temporary cache files
- Partial results during batch processing
- Debug outputs

## Archive

**Description**: Data that is preserved for historical reference but is not actively used.

**Characteristics**:
- No longer needed for active analysis
- Preserved for compliance, reference, or potential future use
- Often stored on lower-cost, slower-access storage
- May be compressed or stored in specialized archival formats

**Examples**:
- Completed project data
- Data from published studies
- Historical datasets
- Backup copies of important data

## Custom

**Description**: Data that doesn't fit into the standard categories and has a specialized role.

**Characteristics**:
- Serves a purpose specific to a particular research workflow
- May combine aspects of multiple standard categories
- Requires custom handling or processing
- Often needs additional documentation to clarify its role

**Examples**:
- Specialized simulation outputs
- Custom visualization data
- Hybrid data products
- Project-specific data types

## Usage Guidelines

When assigning a category to a data location:

1. Consider the role of the data in your research workflow
2. Think about how tools should handle the data (read-only vs. modifiable)
3. Choose the most specific applicable category
4. Use consistent categorization across related data locations
5. Document any custom categories clearly

The category affects how tools interact with the data, including:
- Default access permissions (e.g., raw data might be read-only)
- Storage tier recommendations
- Backup and archiving policies
- Data provenance tracking
