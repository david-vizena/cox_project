import os
import json
from src.services.incident_service import IncidentService
from src.aws.datadog_client import DatadogClient
from src.storage.dynamodb_store import DynamoDBStore


def lambda_handler(event, context):
    """
    AWS Lambda handler that syncs Datadog alerts to DynamoDB.
    """
    try:
        # Use DynamoDB for storage (Lambda should always use cloud storage)
        store = DynamoDBStore()

        # Create Datadog client (uses env vars from Lambda config)
        datadog_client = DatadogClient()

        # Create service and sync
        service = IncidentService(datadog_client=datadog_client, store=store)
        new_incidents = service.sync_datadog_alerts()

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully synced {len(new_incidents)} new incident(s)',
                'new_incidents': len(new_incidents)
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }
