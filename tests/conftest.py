import json
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).parent.parent
SCHEMA_PATH = REPO_ROOT / "schema" / "DatasetStructureModel.schema.json"
EXAMPLES_DIR = REPO_ROOT / "examples"


@pytest.fixture(scope="session")
def schema():
    with SCHEMA_PATH.open() as f:
        return json.load(f)


@pytest.fixture(scope="session")
def example_files():
    return sorted(EXAMPLES_DIR.glob("*.json"))
