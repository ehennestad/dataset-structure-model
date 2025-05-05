# Dataset Structure Model

## Overview

The "Dataset Structure Model" is a configuration framework for describing the structure of scientific datasets, capturing both their physical layout on disk and their semantic organization. It provides a standardized way to describe data locations, their hierarchical organization, and methods for extracting metadata from file paths. It enables standardized representation of, and access to heterogeneous datasets, whether flat or hierarchical, to facilitate interoperability, automation, and reproducibility across tools and research workflows.

This model aims to be useful for scientific research, data analysis pipelines, and any application that deals with complex data hierarchies across multiple storage locations or computing environments.

## Key Components

### Data Locations

Each data location in the model represents a specific type of data with its own organization structure. Data locations include:

- **Display name and identifier**: Human-readable name and unique ID
- **Category**: Classification of the data's role (raw, processed, derived, etc.)
- **Storage paths**: Physical file system locations across different environments
- **Path template**: Template showing the expected structure with placeholders
- **Hierarchy definition**: Specification of the folder structure levels
- **Metadata extractors**: Rules for extracting metadata from paths

### Storage Paths

Storage paths define where data is physically located across different environments:

- **Path ID and location path**: Unique identifier and actual file system path
- **Environment**: Computing environment this path is valid for (e.g., 'windows-lab', 'mac-home')
- **Storage type**: Type of storage medium (local, external, network, cloud, etc.)
- **Priority**: Order of preference when multiple valid paths exist
- **Availability**: Whether the storage location is currently accessible

### Hierarchy Definition

The hierarchy definition specifies the folder structure of a data location:

- **Level name and entity type**: Name and type of entity this level represents
- **Match pattern**: Regular expression for matching valid folders
- **Exclude patterns**: Patterns for folders to exclude
- **Required/Variable flags**: Whether levels must exist and can have variable names
- **Fixed name**: Specific folder name for non-variable levels
- **Metadata mapping**: Mapping between folder patterns and metadata values

### Metadata Extractors

Metadata extractors define how to extract metadata from paths:

- **Metadata field**: Name of the metadata field to extract
- **Extraction method**: Method for extracting the value (substring, regex, function, etc.)
- **Extraction pattern**: Pattern for extraction
- **Data type**: Expected data type of the extracted value
- **Validation**: Rules for validating the extracted value

## Example Use Cases

### Neuroscience Research Data

The model can organize two-photon imaging data with:
- Subjects as the top level
- Sessions within each subject
- Raw and processed data folders
- Metadata extraction for subject IDs, session dates, and experiment details

### Clinical Trial Data

The model can manage clinical trial data with:
- Study as the top level
- Sites within each study
- Patients within each site
- Visits within each patient
- Different data types (imaging, lab results, questionnaires) at the lowest level

### Multi-environment Data Processing

The model supports data processing workflows where:
- Raw data is collected on lab computers
- Processing happens on high-performance computing clusters
- Analysis occurs on researchers' personal workstations
- Each environment has different paths to the same logical data
