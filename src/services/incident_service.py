from src.models.incident import Incident
from src.storage.json_store import IncidentStore
from typing import List


class IncidentService:
    """Service that connects Datadog alerts to our incident system."""

    def __init__(self, datadog_client=None, store: IncidentStore = None):
        """Initialize the service.

        Args:
            datadog_client: DatadogClient or MockDatadogClient instance
            store: IncidentStore instance (creates one if not provided)
        """
        self.datadog_client = datadog_client
        self.store = store or IncidentStore()

    def sync_datadog_alerts(self) -> List[Incident]:
        """Fetch alerts from Datadog and create incidents for them.

        Returns a list of newly created incidents.
        """
        if not self.datadog_client:
            print("No Datadog client configured. Use MockDatadogClient for testing.")
            return []

        # Fetch alerts from Datadog (already simplified dicts)
        alerts = self.datadog_client.get_active_alerts()

        new_incidents: List[Incident] = []

        for alert in alerts:
            # Skip if we already have an incident for this Datadog alert
            existing = self.store.find_by_datadog_alert_id(alert["id"])
            if existing:
                continue

            # Create new incident from Datadog alert
            incident = self._create_incident_from_alert(alert)

            # Save it
            self.store.save(incident)
            new_incidents.append(incident)

        return new_incidents

    def _create_incident_from_alert(self, alert: dict) -> Incident:
        """Convert a Datadog alert dictionary into an Incident object."""
        # Map Datadog alert state to severity
        severity_map = {
            "Alert": 5,  # Critical
            "Warn": 3,  # Medium
            "No Data": 2,  # Low
        }

        alert_state = alert.get("state", "Alert")
        severity = severity_map.get(alert_state, 4)  # Default to 4 if unknown

        # Create incident
        incident = Incident(
            title=alert.get("name", "Unknown Alert"),
            description=alert.get("message", "No description"),
            severity=severity,
            source="datadog",
            datadog_alert_id=alert.get("id"),
        )

        # Add tags from Datadog if available
        if alert.get("tags"):
            incident.tags = alert.get("tags", [])

        return incident

    def get_all_incidents(self) -> List[Incident]:
        """Get all incidents from storage."""
        return self.store.load_all()

    def get_active_incidents(self) -> List[Incident]:
        """Get all incidents that are not yet resolved."""
        detected = self.store.find_by_status("detected")
        acknowledged = self.store.find_by_status("acknowledged")
        return detected + acknowledged
