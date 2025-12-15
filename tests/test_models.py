"""Test Incident and Metric models."""
import pytest
from datetime import datetime

from src.models.incident import Incident
from src.models.metric import Metric


class TestIncident:
    """Test Incident model."""

    def test_create_incident(self):
        """Test creating a new incident."""
        incident = Incident(
            title="Test Incident",
            description="Test description",
            severity=4,
            source="test"
        )

        assert incident.title == "Test Incident"
        assert incident.description == "Test description"
        assert incident.severity == 4
        assert incident.source == "test"
        assert incident.status == "detected"
        assert incident.id is not None
        assert isinstance(incident.detected_at, datetime)
        assert incident.acknowledged_at is None
        assert incident.resolved_at is None

    def test_acknowledge_incident(self):
        """Test acknowledging an incident."""
        incident = Incident(
            title="Test",
            description="Test",
            severity=3
        )

        incident.acknowledge("John Doe")

        assert incident.status == "acknowledged"
        assert incident.assignee == "John Doe"
        assert incident.acknowledged_at is not None
        assert isinstance(incident.acknowledged_at, datetime)

    def test_acknowledge_wrong_status(self):
        """Test that acknowledging a non-detected incident fails."""
        incident = Incident(
            title="Test",
            description="Test",
            severity=3
        )
        incident.acknowledge("John")
        incident.resolve("Fixed", ["Step 1"])

        # Try to acknowledge a resolved incident
        with pytest.raises(ValueError):
            incident.acknowledge("John")

    def test_resolve_incident(self):
        """Test resolving an incident."""
        incident = Incident(
            title="Test",
            description="Test",
            severity=3
        )

        incident.resolve("Root cause", ["Step 1", "Step 2"])

        assert incident.status == "resolved"
        assert incident.root_cause == "Root cause"
        assert incident.resolution_steps == ["Step 1", "Step 2"]
        assert incident.resolved_at is not None

    def test_resolve_from_acknowledged(self):
        """Test resolving an acknowledged incident."""
        incident = Incident(
            title="Test",
            description="Test",
            severity=3
        )
        incident.acknowledge("John")
        incident.resolve("Root cause", ["Step 1"])

        assert incident.status == "resolved"

    def test_resolve_wrong_status(self):
        """Test that resolving a resolved incident fails."""
        incident = Incident(
            title="Test",
            description="Test",
            severity=3
        )
        incident.resolve("Root cause", ["Step 1"])

        # Try to resolve again
        with pytest.raises(ValueError):
            incident.resolve("Another cause", ["Step 2"])

    def test_to_dict(self):
        """Test converting incident to dictionary."""
        incident = Incident(
            title="Test",
            description="Test",
            severity=3,
            datadog_alert_id="alert-123"
        )
        incident.acknowledge("John")

        data = incident.to_dict()

        assert data["title"] == "Test"
        assert data["severity"] == 3
        assert data["status"] == "acknowledged"
        assert data["assignee"] == "John"
        assert data["datadog_alert_id"] == "alert-123"
        assert isinstance(data["detected_at"], str)
        assert isinstance(data["acknowledged_at"], str)

    def test_from_dict(self):
        """Test creating incident from dictionary."""
        data = {
            "id": "test-id",
            "title": "Test",
            "description": "Test",
            "severity": 3,
            "source": "test",
            "status": "acknowledged",
            "assignee": "John",
            "detected_at": "2024-01-01T12:00:00",
            "acknowledged_at": "2024-01-01T13:00:00",
            "resolved_at": None,
            "root_cause": None,
            "resolution_steps": [],
            "tags": [],
            "datadog_alert_id": None
        }

        incident = Incident.from_dict(data)

        assert incident.id == "test-id"
        assert incident.title == "Test"
        assert incident.status == "acknowledged"
        assert incident.assignee == "John"
        assert isinstance(incident.detected_at, datetime)
        assert isinstance(incident.acknowledged_at, datetime)

    def test_str_representation(self):
        """Test string representation of incident."""
        incident = Incident(
            title="Test Incident",
            description="Test",
            severity=3
        )

        str_repr = str(incident)
        assert "Test Incident" in str_repr
        assert incident.id in str_repr
        assert "detected" in str_repr


class TestMetric:
    """Test Metric model."""

    def test_create_metric(self):
        """Test creating a new metric."""
        metric = Metric(
            name="cpu.usage",
            value=85.5,
            unit="percent"
        )

        assert metric.name == "cpu.usage"
        assert metric.value == 85.5
        assert metric.unit == "percent"
        assert metric.id is not None
        assert isinstance(metric.timestamp, datetime)
        assert metric.tags == {}
        assert metric.source == "datadog"

    def test_metric_with_tags(self):
        """Test creating metric with tags."""
        metric = Metric(
            name="memory.used",
            value=1024,
            unit="bytes",
            tags={"host": "server-01", "env": "production"}
        )

        assert metric.tags == {"host": "server-01", "env": "production"}

    def test_metric_to_dict(self):
        """Test converting metric to dictionary."""
        metric = Metric(
            name="cpu.usage",
            value=85.5,
            unit="percent"
        )

        data = metric.to_dict()

        assert data["name"] == "cpu.usage"
        assert data["value"] == 85.5
        assert data["unit"] == "percent"
        assert isinstance(data["timestamp"], str)

    def test_metric_from_dict(self):
        """Test creating metric from dictionary."""
        data = {
            "id": "test-id",
            "name": "cpu.usage",
            "value": 85.5,
            "unit": "percent",
            "tags": {"host": "server-01"},
            "timestamp": "2024-01-01T12:00:00",
            "source": "datadog"
        }

        metric = Metric.from_dict(data)

        assert metric.id == "test-id"
        assert metric.name == "cpu.usage"
        assert metric.value == 85.5
        assert isinstance(metric.timestamp, datetime)
