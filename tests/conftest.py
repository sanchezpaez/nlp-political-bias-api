"""Shared pytest fixtures for training script tests.

This file intentionally starts with prepare-corpus fixtures only.
Additional script fixtures will be added incrementally, script by script.
"""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_module(relative_path: str, module_name: str) -> ModuleType:
	"""Load a Python module from a file path inside the repository."""
	module_path = PROJECT_ROOT / relative_path
	spec = spec_from_file_location(module_name, module_path)
	if spec is None or spec.loader is None:
		raise RuntimeError(f"Cannot load module from {module_path}")
	module = module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


@pytest.fixture(scope="session")
def prepare_module():
    """Provide the loaded training/prepare_corpus.py module for tests."""
    return _load_module("training/prepare_corpus.py", "prepare_corpus_module")


@pytest.fixture(scope="session")
def download_module():
	"""Provide the loaded training/download_corpus.py module for tests."""
	return _load_module("training/download_corpus.py", "download_corpus_module")
