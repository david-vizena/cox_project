from src.models.incident import Incident
from src.storage.json_store import IncidentStore

# Create a store
store = IncidentStore()

# Create an incident
incident1 = Incident(
    title="Database Connection Timeout",
    description="Users unable to connect to primary database",
    severity=4,
    source="datadog"
)

print("Created incident:")
print(f"  ID: {incident1.id}")
print(f"  Title: {incident1.title}")
print(f"  Status: {incident1.status}")

# Save it
store.save(incident1)
print("\n✅ Incident saved!")

# Load it back
all_incidents = store.load_all()
print(f"\n✅ Loaded {len(all_incidents)} incident(s)")

# Find it by ID
found = store.find_by_id(incident1.id)
if found:
    print(f"\n✅ Found incident: {found.title}")

# Test acknowledging it
incident1.acknowledge("David")
store.save(incident1)
print(f"\n✅ Incident acknowledged by: {incident1.assignee}")

# Test finding by status
active = store.find_by_status("acknowledged")
print(f"\n✅ Found {len(active)} acknowledged incident(s)")
