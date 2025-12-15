import os

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from typing import List, Optional

from src.models.incident import Incident


class DynamoDBStore:
    """
    AWS DynamoDB storage implementation for incidents.
    Production-ready storage that scales and persists in the cloud.
    """

    def __init__(self, table_name: str = None, region: str = "us-east-1"):
        """
        Initialize DynamoDB storage.

        Args:
            table_name: Name of the DynamoDB table (defaults to env var or 'incidents')
            region: AWS region (defaults to us-east-1)
        """
        self.table_name = table_name or os.getenv(
            "DYNAMODB_TABLE_NAME", "incidents")
        self.region = region

        # Initialize DynamoDB client
        self.dynamodb = boto3.resource("dynamodb", region_name=self.region)
        self.table = self.dynamodb.Table(self.table_name)

        # Create table if it doesn't exist
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Create the DynamoDB table if it doesn't exist."""
        try:
            self.table.meta.client.describe_table(TableName=self.table_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                self._create_table()
            else:
                raise

    def _create_table(self):
        """Create the DynamoDB table with proper schema."""
        try:
            # Note: AttributeDefinitions must be declared at the *table* level,
            # not inside each GlobalSecondaryIndex definition.
            self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {"AttributeName": "id", "KeyType": "HASH"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "id", "AttributeType": "S"},
                    {"AttributeName": "status", "AttributeType": "S"},
                    {"AttributeName": "datadog_alert_id", "AttributeType": "S"},
                ],
                BillingMode="PAY_PER_REQUEST",
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "status-index",
                        "KeySchema": [
                            {"AttributeName": "status", "KeyType": "HASH"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                    },
                    {
                        "IndexName": "datadog-alert-id-index",
                        "KeySchema": [
                            {"AttributeName": "datadog_alert_id", "KeyType": "HASH"},
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                    },
                ],
            )
            self.table.meta.client.get_waiter("table_exists").wait(
                TableName=self.table_name
            )
            print(f"[OK] Created DynamoDB table: {self.table_name}")
        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceInUseException":
                raise

    def save(self, incident: Incident):
        """Save an incident to DynamoDB."""
        try:
            item = incident.to_dict()
            item = {k: v if v is not None else "" for k, v in item.items()}
            # Ensure datadog_alert_id is always a string (GSI schema expects string type)
            if "datadog_alert_id" in item and item["datadog_alert_id"]:
                item["datadog_alert_id"] = str(item["datadog_alert_id"])
            self.table.put_item(Item=item)
        except ClientError as e:
            raise Exception(f"Error saving incident to DynamoDB: {e}")

    def load_all(self) -> List[Incident]:
        """Load all incidents from DynamoDB."""
        try:
            response = self.table.scan()
            incidents = []
            for item in response.get("Items", []):
                item = {k: v if v != "" else None for k, v in item.items()}
                incident = Incident.from_dict(item)
                incidents.append(incident)

            while "LastEvaluatedKey" in response:
                response = self.table.scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"]
                )
                for item in response.get("Items", []):
                    item = {k: v if v != "" else None for k, v in item.items()}
                    incident = Incident.from_dict(item)
                    incidents.append(incident)

            return incidents
        except ClientError as e:
            raise Exception(f"Error loading incidents from DynamoDB: {e}")

    def find_by_id(self, incident_id: str) -> Optional[Incident]:
        """Find an incident by its ID."""
        try:
            response = self.table.get_item(Key={"id": incident_id})
            if "Item" in response:
                item = response["Item"]
                item = {k: v if v != "" else None for k, v in item.items()}
                return Incident.from_dict(item)
            return None
        except ClientError as e:
            raise Exception(f"Error finding incident in DynamoDB: {e}")

    def find_by_status(self, status: str) -> List[Incident]:
        """Find all incidents with a specific status using GSI."""
        try:
            response = self.table.query(
                IndexName="status-index",
                KeyConditionExpression=Key("status").eq(status),
            )
            incidents = []
            for item in response.get("Items", []):
                item = {k: v if v != "" else None for k, v in item.items()}
                incident = Incident.from_dict(item)
                incidents.append(incident)
            return incidents
        except ClientError as e:
            raise Exception(f"Error querying incidents by status: {e}")

    def find_by_datadog_alert_id(self, alert_id: str) -> Optional[Incident]:
        """Find an incident by its Datadog alert ID using GSI."""
        if not alert_id:
            return None
        try:
            # Ensure alert_id is a string (DynamoDB schema expects string type)
            alert_id_str = str(alert_id)
            response = self.table.query(
                IndexName="datadog-alert-id-index",
                KeyConditionExpression=Key(
                    "datadog_alert_id").eq(alert_id_str),
            )
            if response.get("Items"):
                item = response["Items"][0]
                item = {k: v if v != "" else None for k, v in item.items()}
                return Incident.from_dict(item)
            return None
        except ClientError as e:
            raise Exception(f"Error finding incident by Datadog alert ID: {e}")
