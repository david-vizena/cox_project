"""Test Datadog client implementations."""
import pytest

from src.aws.mock_datadog_client import MockDatadogClient


class TestMockDatadogClient:
    """Test MockDatadogClient."""

    def test_init(self):
        """Test initializing mock client."""
        client = MockDatadogClient()
        assert client is not None
        assert hasattr(client, 'mock_alerts')

    def test_get_active_alerts(self):
        """Test getting active alerts from mock client."""
        client = MockDatadogClient()
        alerts = client.get_active_alerts()

        assert len(alerts) == 3
        assert all(isinstance(alert, dict) for alert in alerts)

        # Check structure
        for alert in alerts:
            assert 'id' in alert
            assert 'name' in alert
            assert 'message' in alert
            assert 'state' in alert
            assert 'tags' in alert

    def test_get_active_alerts_content(self):
        """Test content of mock alerts."""
        client = MockDatadogClient()
        alerts = client.get_active_alerts()

        # Check specific alerts exist
        alert_names = [alert['name'] for alert in alerts]
        assert 'High CPU Usage' in alert_names
        assert 'Database Connection Pool Exhausted' in alert_names
        assert 'API Response Time Degraded' in alert_names

    def test_get_recent_events(self):
        """Test getting recent events from mock client."""
        client = MockDatadogClient()
        events = client.get_recent_events()

        assert len(events) == 1
        assert isinstance(events[0], dict)
        assert 'id' in events[0]
        assert 'title' in events[0]
        assert 'text' in events[0]

    def test_get_recent_events_with_hours(self):
        """Test getting events with custom hours parameter."""
        client = MockDatadogClient()
        events = client.get_recent_events(hours=48)

        # Mock client doesn't filter by hours, but should still work
        assert len(events) >= 0
