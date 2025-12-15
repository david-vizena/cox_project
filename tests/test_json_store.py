"""Test JSON storage implementation."""
import pytest

from src.models.incident import Incident
from src.storage.json_store import IncidentStore


class TestJSONStore:
    """Test JSON store functionality."""

    def test_save_and_load_incident(self, json_store, sample_incident):
        """Test saving and loading an incident."""
        # Save
        json_store.save(sample_incident)

        # Load
        incidents = json_store.load_all()

        assert len(incidents) == 1
        assert incidents[0].id == sample_incident.id
        assert incidents[0].title == sample_incident.title

    def test_save_updates_existing(self, json_store, sample_incident):
        """Test that saving an existing incident updates it."""
        json_store.save(sample_incident)

        # Modify and save again
        sample_incident.acknowledge("John")
        json_store.save(sample_incident)

        # Load and verify
        incidents = json_store.load_all()
        assert len(incidents) == 1
        assert incidents[0].status == "acknowledged"
        assert incidents[0].assignee == "John"

    def test_find_by_id(self, json_store, sample_incident):
        """Test finding an incident by ID."""
        json_store.save(sample_incident)

        found = json_store.find_by_id(sample_incident.id)

        assert found is not None
        assert found.id == sample_incident.id
        assert found.title == sample_incident.title

    def test_find_by_id_not_found(self, json_store):
        """Test finding a non-existent incident."""
        found = json_store.find_by_id("non-existent-id")
        assert found is None

    def test_find_by_status(self, json_store):
        """Test finding incidents by status."""
        # Create multiple incidents with different statuses
        incident1 = Incident("Test 1", "Desc", 3)
        incident2 = Incident("Test 2", "Desc", 3)
        incident3 = Incident("Test 3", "Desc", 3)

        incident1.acknowledge("John")
        incident2.acknowledge("Jane")
        # incident3 stays detected

        json_store.save(incident1)
        json_store.save(incident2)
        json_store.save(incident3)

        # Find acknowledged
        acknowledged = json_store.find_by_status("acknowledged")
        assert len(acknowledged) == 2

        # Find detected
        detected = json_store.find_by_status("detected")
        assert len(detected) == 1
        assert detected[0].id == incident3.id

    def test_find_by_datadog_alert_id(self, json_store):
        """Test finding an incident by Datadog alert ID."""
        incident = Incident(
            "Test",
            "Desc",
            3,
            source="datadog",
            datadog_alert_id="alert-123"
        )
        json_store.save(incident)

        found = json_store.find_by_datadog_alert_id("alert-123")

        assert found is not None
        assert found.datadog_alert_id == "alert-123"

    def test_find_by_datadog_alert_id_not_found(self, json_store):
        """Test finding a non-existent Datadog alert ID."""
        found = json_store.find_by_datadog_alert_id("non-existent")
        assert found is None

    def test_load_all_empty(self, json_store):
        """Test loading from empty storage."""
        incidents = json_store.load_all()
        assert incidents == []

    def test_multiple_incidents(self, json_store):
        """Test saving and loading multiple incidents."""
        incidents = [
            Incident(f"Test {i}", f"Desc {i}", 3)
            for i in range(5)
        ]

        for incident in incidents:
            json_store.save(incident)

        loaded = json_store.load_all()
        assert len(loaded) == 5

    def test_persistence(self, temp_storage_dir):
        """Test that data persists across store instances."""
        # Create first store and save
        store1 = IncidentStore(storage_dir=temp_storage_dir)
        incident = Incident("Test", "Desc", 3)
        store1.save(incident)

        # Create second store and load
        store2 = IncidentStore(storage_dir=temp_storage_dir)
        loaded = store2.load_all()

        assert len(loaded) == 1
        assert loaded[0].id == incident.id
