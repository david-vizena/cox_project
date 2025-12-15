"""Shared pytest fixtures."""
import os
import tempfile
import shutil
from pathlib import Path

import pytest

from src.models.incident import Incident
from src.storage.json_store import IncidentStore
from src.aws.mock_datadog_client import MockDatadogClient


@pytest.fixture
def temp_storage_dir():
    """Create a temporary directory for test storage."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def json_store(temp_storage_dir):
    """Create a JSON store with temporary storage."""
    return IncidentStore(storage_dir=temp_storage_dir)


@pytest.fixture
def sample_incident():
    """Create a sample incident for testing."""
    return Incident(
        title="Test Incident",
        description="This is a test incident",
        severity=3,
        source="test"
    )


@pytest.fixture
def mock_datadog_client():
    """Create a mock Datadog client."""
    return MockDatadogClient()
