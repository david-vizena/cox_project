from typing import List


class MockDatadogClient:
    """
    Mock Datadog client that returns fake alerts for testing.
    Use this when you don't have Datadog credentials yet.
    """

    def __init__(self):
        """Initialize with some fake alerts."""
        self.mock_alerts = [
            {
                'id': 'alert-001',
                'name': 'High CPU Usage',
                'message': 'CPU usage is above 90% on server-01',
                'state': 'Alert',
                'tags': ['env:production', 'team:backend']
            },
            {
                'id': 'alert-002',
                'name': 'Database Connection Pool Exhausted',
                'message': 'PostgreSQL connection pool is at 100% capacity',
                'state': 'Alert',
                'tags': ['env:production', 'service:database']
            },
            {
                'id': 'alert-003',
                'name': 'API Response Time Degraded',
                'message': 'P95 response time is above 500ms',
                'state': 'Warn',
                'tags': ['env:production', 'team:api']
            }
        ]

    def get_active_alerts(self) -> List[dict]:
        """
        Return fake alerts for testing.
        """
        return self.mock_alerts

    def get_recent_events(self, hours: int = 24) -> List[dict]:
        """
        Return fake events for testing.
        """
        return [
            {
                'id': 'event-001',
                'title': 'Deployment Completed',
                'text': 'Version 2.3.1 deployed to production',
                'date_happened': 1234567890,
                'priority': 'normal',
                'tags': ['deployment', 'production']
            }
        ]
