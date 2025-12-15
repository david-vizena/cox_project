"""Test IncidentService."""
import pytest

from src.services.incident_service import IncidentService
from src.storage.json_store import IncidentStore
from src.aws.mock_datadog_client import MockDatadogClient
from src.models.incident import Incident


class TestIncidentService:
    """Test IncidentService functionality."""

    def test_init_without_client(self, json_store):
        """Test initializing service without Datadog client."""
        service = IncidentService(store=json_store)

        assert service.datadog_client is None
        assert service.store is not None

    def test_init_with_mock_client(self, json_store, mock_datadog_client):
        """Test initializing service with mock client."""
        service = IncidentService(
            datadog_client=mock_datadog_client,
            store=json_store
        )

        assert service.datadog_client is not None
        assert service.store is not None

    def test_sync_without_client(self, json_store):
        """Test syncing without Datadog client returns empty list."""
        service = IncidentService(store=json_store)

        new_incidents = service.sync_datadog_alerts()

        assert new_incidents == []

    def test_sync_creates_incidents(self, json_store, mock_datadog_client):
        """Test syncing creates incidents from alerts."""
        service = IncidentService(
            datadog_client=mock_datadog_client,
            store=json_store
        )

        new_incidents = service.sync_datadog_alerts()

        # Mock client has 3 alerts
        assert len(new_incidents) == 3
        assert all(isinstance(inc, Incident) for inc in new_incidents)

    def test_sync_skips_duplicates(self, json_store, mock_datadog_client):
        """Test that syncing twice doesn't create duplicates."""
        service = IncidentService(
            datadog_client=mock_datadog_client,
            store=json_store
        )

        # First sync
        new_incidents_1 = service.sync_datadog_alerts()
        assert len(new_incidents_1) == 3

        # Second sync - should skip duplicates
        new_incidents_2 = service.sync_datadog_alerts()
        assert len(new_incidents_2) == 0

        # Verify total count
        all_incidents = service.get_all_incidents()
        assert len(all_incidents) == 3

    def test_sync_maps_alert_states_to_severity(self, json_store, mock_datadog_client):
        """Test that alert states are correctly mapped to severity."""
        service = IncidentService(
            datadog_client=mock_datadog_client,
            store=json_store
        )

        new_incidents = service.sync_datadog_alerts()

        # Check severity mapping
        # Alert -> 5 (Critical)
        # Warn -> 3 (Medium)
        alert_incidents = [
            inc for inc in new_incidents if "High CPU" in inc.title or "Database" in inc.title]
        assert all(inc.severity == 5 for inc in alert_incidents)

        warn_incidents = [
            inc for inc in new_incidents if "API Response" in inc.title]
        assert all(inc.severity == 3 for inc in warn_incidents)

    def test_sync_preserves_tags(self, json_store, mock_datadog_client):
        """Test that tags from alerts are preserved."""
        service = IncidentService(
            datadog_client=mock_datadog_client,
            store=json_store
        )

        new_incidents = service.sync_datadog_alerts()

        # Check that incidents have tags
        assert all(hasattr(inc, 'tags') for inc in new_incidents)
        assert any(len(inc.tags) > 0 for inc in new_incidents)

    def test_get_all_incidents(self, json_store, mock_datadog_client):
        """Test getting all incidents."""
        service = IncidentService(
            datadog_client=mock_datadog_client,
            store=json_store
        )

        service.sync_datadog_alerts()

        all_incidents = service.get_all_incidents()
        assert len(all_incidents) == 3

    def test_get_active_incidents(self, json_store, mock_datadog_client):
        """Test getting active (non-resolved) incidents."""
        service = IncidentService(
            datadog_client=mock_datadog_client,
            store=json_store
        )

        service.sync_datadog_alerts()

        # All should be active (detected status)
        active = service.get_active_incidents()
        assert len(active) == 3

        # Resolve one
        all_incidents = service.get_all_incidents()
        all_incidents[0].resolve("Fixed", ["Step 1"])
        json_store.save(all_incidents[0])

        # Should now have 2 active
        active = service.get_active_incidents()
        assert len(active) == 2

    def test_get_active_includes_acknowledged(self, json_store, mock_datadog_client):
        """Test that active incidents include acknowledged ones."""
        service = IncidentService(
            datadog_client=mock_datadog_client,
            store=json_store
        )

        service.sync_datadog_alerts()

        # Acknowledge one
        all_incidents = service.get_all_incidents()
        all_incidents[0].acknowledge("John")
        json_store.save(all_incidents[0])

        # Should still be active
        active = service.get_active_incidents()
        assert len(active) == 3
