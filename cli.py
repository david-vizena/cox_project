import click

from src.services.incident_service import IncidentService
from src.aws.datadog_client import DatadogClient


def build_service() -> IncidentService:
    """Create an IncidentService wired to the real Datadog client."""
    datadog_client = DatadogClient()
    service = IncidentService(datadog_client=datadog_client)
    return service


@click.group()
def cli():
    """Incident management CLI."""
    pass


@cli.command()
def sync():
    """Sync Datadog alerts into incidents."""
    service = build_service()

    click.echo("Syncing Datadog alerts to incidents...")
    new_incidents = service.sync_datadog_alerts()
    click.echo(f"Created {len(new_incidents)} new incident(s)")

    for inc in new_incidents:
        click.echo("")
        click.echo(f"Incident: {inc.title}")
        click.echo(f"  ID: {inc.id}")
        click.echo(f"  Severity: {inc.severity}")
        click.echo(f"  Status: {inc.status}")
        click.echo(f"  Datadog Alert ID: {inc.datadog_alert_id}")


@cli.command()
def list():
    """List all incidents in storage."""
    service = build_service()
    incidents = service.get_all_incidents()

    if not incidents:
        click.echo("No incidents found.")
        return

    click.echo(f"Found {len(incidents)} incident(s):\n")

    for inc in incidents:
        short_id = inc.id[:8]
        click.echo(
            f"{short_id} | {inc.title} | sev={inc.severity} | status={inc.status}")


if __name__ == "__main__":
    cli()
