from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.api.events_api import EventsApi
import os
from dotenv import load_dotenv

# Load env vars from .env file
load_dotenv()


class DatadogClient:
    """Wrapper class for Datadog API interactions."""

    def __init__(self):
        """Initialize the Datadog API client with credentials."""
        # Get API key and app key from env vars
        api_key = os.getenv("DATADOG_API_KEY")
        app_key = os.getenv("DATADOG_APP_KEY")
        site = os.getenv("DATADOG_SITE", "datadoghq.com")  # Default to US site

        if not api_key or not app_key:
            raise ValueError(
                "DATADOG_API_KEY and DATADOG_APP_KEY must be set in environment"
            )

        # Configure the Datadog API client
        configuration = Configuration()
        configuration.api_key["apiKeyAuth"] = api_key
        configuration.api_key["appKeyAuth"] = app_key
        configuration.server_variables["site"] = site

        # Create the API client
        self.api_client = ApiClient(configuration)
        self.monitors_api = MonitorsApi(self.api_client)
        self.events_api = EventsApi(self.api_client)

    def get_active_alerts(self):
        """Fetch monitors from Datadog and return them as simple dicts."""
        try:
            response = self.monitors_api.list_monitors()

            alerts = []
            for monitor in response:
                raw_state = getattr(monitor, "overall_state", None)
                # Convert enum-like state (e.g. MonitorOverallStates.ALERT) to a simple string
                if raw_state is not None:
                    state = str(raw_state).split(".")[-1]
                else:
                    state = None

                alerts.append(
                    {
                        "id": monitor.id,
                        "name": monitor.name,
                        "message": monitor.message,
                        "state": state,
                        "tags": monitor.tags if hasattr(monitor, "tags") else [],
                    }
                )

            return alerts
        except Exception as e:
            print(f"Error fetching alerts: {e}")
            return []

    def get_recent_events(self, hours: int = 24):
        """Fetch recent events from Datadog."""
        try:
            from datetime import datetime, timedelta

            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)

            # Fetch events
            response = self.events_api.list_events(
                start=int(start_time.timestamp()),
                end=int(end_time.timestamp()),
            )

            # Format events
            events = []
            for event in response.events:
                events.append(
                    {
                        "id": event.id,
                        "title": event.title,
                        "text": event.text,
                        "date_happened": event.date_happened,
                        "priority": event.priority,
                        "tags": event.tags if hasattr(event, "tags") else [],
                    }
                )

            return events
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
