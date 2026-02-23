import json
import sys
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
LIB_DIR = Path(__file__).parent.parent / "lib"

# Make lib/ importable
sys.path.insert(0, str(LIB_DIR))


@pytest.fixture
def fixtures():
    """Load all fixture files into a dict keyed by stem name."""
    data = {}
    for f in FIXTURES_DIR.glob("*.json"):
        data[f.stem] = json.loads(f.read_text())
    # raw_output is plain text
    raw_path = FIXTURES_DIR / "raw_output.txt"
    if raw_path.exists():
        data["raw_output"] = raw_path.read_text()
    return data
