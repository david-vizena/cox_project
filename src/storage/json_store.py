import json
from pathlib import Path
from typing import List, Optional
from src.models.incident import Incident


class IncidentStore:
    """
    Handles storage and retrieval of incidents.
    Currently uses JSON files, but designed to be easily migrated to DynamoDB.
    """

    def __init__(self, storage_dir: str = "data"):
        """
        Initialize the storage.

        Args:
            storage_dir: Directory where incident files will be stored
        """
        self.storage_dir = Path(storage_dir)
        # Create directory if it doesn't exist
        self.storage_dir.mkdir(exist_ok=True)
        self.incidents_file = self.storage_dir / "incidents.json"

    def save(self, incident: Incident):
        """
        Save an incident to storage.
        If it already exists (same ID), update it. Otherwise, add it.
        """
        incidents = self.load_all()

        # Check if incident already exists
        existing_index = None
        for i, existing in enumerate(incidents):
            if existing.id == incident.id:
                existing_index = i
                break

        if existing_index is not None:
            # Update existing incident
            incidents[existing_index] = incident
        else:
            # Add new incident
            incidents.append(incident)

        # Save all incidents back to file
        self._write_to_file(incidents)

    def load_all(self) -> List[Incident]:
        """
        Load all incidents from storage.
        Returns empty list if no incidents exist.
        """
        if not self.incidents_file.exists():
            return []

        try:
            with open(self.incidents_file, 'r') as f:
                data = json.load(f)

            # Convert dictionaries back to Incident objects
            incidents = []
            for incident_data in data:
                # HERE'S WHERE from_dict IS USED!
                incident = Incident.from_dict(incident_data)
                incidents.append(incident)

            return incidents
        except json.JSONDecodeError:
            # File exists but is corrupted/invalid JSON
            return []

    def find_by_id(self, incident_id: str) -> Optional[Incident]:
        """
        Find an incident by its ID.
        Returns None if not found.
        """
        incidents = self.load_all()
        for incident in incidents:
            if incident.id == incident_id:
                return incident
        return None

    def find_by_status(self, status: str) -> List[Incident]:
        """
        Find all incidents with a specific status.
        """
        incidents = self.load_all()
        return [inc for inc in incidents if inc.status == status]

    def _write_to_file(self, incidents: List[Incident]):
        """
        Private method to write incidents to JSON file.
        Converts all incidents to dictionaries first.
        """
        # Convert all incidents to dictionaries
        data = [incident.to_dict() for incident in incidents]

        # Write to file
        with open(self.incidents_file, 'w') as f:
            json.dump(data, f, indent=2)
