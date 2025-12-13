from datetime import datetime
from typing import Optional
import uuid


class Incident:
    """
    Represents a production incident.
    Tracks the full lifecycle from detection to resolution.
    """

    def __init__(self, title: str, description: str, severity: int,
                 source: str = "manual", datadog_alert_id: Optional[str] = None):
        """
        Create a new incident.

        Args:
            title: Short description of the incident
            description: Detailed description
            severity: 1-5 (1=low, 5=critical)
            source: Where it came from (manual, datadog, etc.)
            datadog_alert_id: Optional ID from Datadog if created from alert
        """
        # Generate unique ID
        self.id = str(uuid.uuid4())

        # Basic info
        self.title = title
        self.description = description
        self.severity = severity
        self.source = source
        self.datadog_alert_id = datadog_alert_id

        # Status tracking
        self.status = "detected"  # detected, acknowledged, resolved
        self.assignee = None

        # Timestamps
        self.detected_at = datetime.now()
        self.acknowledged_at = None
        self.resolved_at = None

        # Resolution info
        self.root_cause = None
        self.resolution_steps = []
        self.tags = []

    def acknowledge(self, assignee: str):
        """
        Mark incident as acknowledged and assign to someone.
        """
        if self.status != "detected":
            raise ValueError(
                f"Cannot acknowledge incident in {self.status} status")

        self.status = "acknowledged"
        self.assignee = assignee
        self.acknowledged_at = datetime.now()

    def resolve(self, root_cause: str, resolution_steps: list):
        """
        Mark incident as resolved with root cause and steps taken.
        """
        if self.status not in ["detected", "acknowledged"]:
            raise ValueError(
                f"Cannot resolve incident in {self.status} status")

        self.status = "resolved"
        self.root_cause = root_cause
        self.resolution_steps = resolution_steps
        self.resolved_at = datetime.now()

    def to_dict(self):
        """
        Convert incident to dictionary for storage.
        Converts datetime objects to strings for JSON serialization.
        """
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'source': self.source,
            'datadog_alert_id': self.datadog_alert_id,
            'status': self.status,
            'assignee': self.assignee,
            'detected_at': self.detected_at.isoformat() if self.detected_at else None,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'root_cause': self.root_cause,
            'resolution_steps': self.resolution_steps,
            'tags': self.tags
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create an Incident from a dictionary (for loading from storage).
        This is a class method - notice the @classmethod decorator.
        """
        incident = cls(
            title=data['title'],
            description=data['description'],
            severity=data['severity'],
            source=data.get('source', 'manual'),
            datadog_alert_id=data.get('datadog_alert_id')
        )

        # Restore all the fields
        incident.id = data['id']
        incident.status = data['status']
        incident.assignee = data.get('assignee')
        incident.tags = data.get('tags', [])
        incident.root_cause = data.get('root_cause')
        incident.resolution_steps = data.get('resolution_steps', [])

        # Convert ISO strings back to datetime objects
        if data.get('detected_at'):
            incident.detected_at = datetime.fromisoformat(data['detected_at'])
        if data.get('acknowledged_at'):
            incident.acknowledged_at = datetime.fromisoformat(
                data['acknowledged_at'])
        if data.get('resolved_at'):
            incident.resolved_at = datetime.fromisoformat(data['resolved_at'])

        return incident

    def __str__(self):
        """
        String representation of the incident.
        This is what gets printed when you do print(incident)
        """
        return f"Incident {self.id}: {self.title} ({self.status})"
