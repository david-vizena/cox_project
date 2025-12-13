from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.monitors_api import MonitorsApi
from datadog_api_client.v2.api.events_api import EventsApi
import os
from dotenv import load_dotenv

# Load env vars from .env file
load_dotenv()


class DatadogClient:
    """
    Wrapper class for Datadog API interactions.
    This handles authentication and provides methods to fetch alerts and events.
    """

    def __init__(self):
        """
        Initialize the Datadog API client with credentials.
        Pull in from env vars for security
        """
        # Get API key and app key from env vars
        api_key = os.getenv('DATADOG_API_KEY')
        app_key = os.getenv('DATADOG_APP_KEY')
        site = os.getenv('DATADOG_SITE', 'datadoghq.com')  # Default to US site

        if not api_key or not app_key:
            raise ValueError(
                "DATADOG_API_KEY and DATADOG_APP_KEY must be set in environment")

        # Configure the Datadog API client
        configuration = Configuration()
        configuration.api_key['apiKeyAuth'] = api_key
        configuration.api_key['appKeyAuth'] = app_key
        configuration.server_variables['site'] = site

        # Create the API client
        self.api_client = ApiClient(configuration)
        self.monitors_api = MonitorsApi(self.api_client)
        self.events_api = EventsApi(self.api_client)

    def get_active_alerts(self):
        """
        Fetch active/trigger monitors from Datadog.
        These represent potential incidents.
        """
        try:
            # Geta ll monitors, filer for alerting status
            response = self.monitors_api.list_monitors()

            # Filter for monitors that are currently alerting
            active_alerts = []
            for monitor in response:
                if monitor.overall_state in ['Alert', 'Warn']:
                    active_alerts.append({
                        'id': monitor.id,
                        'name': monitor.name,
                        'message': monitor.message,
                        'state': monitor.overall_state,
                        'tags': monitor.tags if hasattr(monitor, 'tags') else []
                    })
            return active_alerts
        except Exception as e:
            print(f"Error fetching alerts: {e}")
            return []

    def get_recent_events(self, hours=24):
        """
        Fetch recent events from Datadog.
        Events can indicate incidents or important system changes.
        """
        try:
            from datetime import datetime, timedelta

            # Calculate time range
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)

            # Fetch events
            response = self.events_api.list_events(
                start=int(start_time.timestamp()),
                end=int(end_time.timestamp())
            )

            # Format events
            events = []
            for event in response.events:
                events.append({
                    'id': event.id,
                    'title': event.title,
                    'text': event.text,
                    'date_happened': event.date_happened,
                    'priority': event.priority,
                    'tags': event.tags if hasattr(event, 'tags') else []
                })

            return events
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
