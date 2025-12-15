from src.services.incident_service import IncidentService
# from src.aws.mock_datadog_client import MockDatadogClient
from src.aws.datadog_client import DatadogClient

# Create mock Datadog client
# Commented out when switched to live Datadog Data

# mock_client = MockDatadogClient()

# Create live Datadog client
datadog_client = DatadogClient()

# Create service with mock client
service = IncidentService(datadog_client=datadog_client)

print("[SYNC] Syncing Datadog alerts to incidents...\n")

# Sync alerts (creates incidents from Datadog alerts)
new_incidents = service.sync_datadog_alerts()

print(f"[OK] Created {len(new_incidents)} new incident(s)\n")

# Show what was created
for incident in new_incidents:
    print(f"Incident: {incident.title}")
    print(f"  ID: {incident.id}")
    print(f"  Severity: {incident.severity}")
    print(f"  Status: {incident.status}")
    print(f"  Datadog Alert ID: {incident.datadog_alert_id}")
    print()

# Get all incidents
all_incidents = service.get_all_incidents()
print(f"[STATS] Total incidents in storage: {len(all_incidents)}")

# Get active incidents
active = service.get_active_incidents()
print(f"[ALERT] Active incidents (not resolved): {len(active)}")

# Test running it again (should not create duplicates)
print("\n[SYNC] Running sync again (should skip duplicates)...")
new_incidents_2 = service.sync_datadog_alerts()
print(f"[OK] Created {len(new_incidents_2)} new incident(s) (should be 0)")
