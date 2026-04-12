from datetime import datetime, UTC
from uuid import uuid4

import boto3
from boto3.dynamodb.conditions import Key


class DynamoDBService:
    def __init__(self, table_name: str, region: str):
        self.table_name = table_name
        self.table = boto3.resource("dynamodb", region_name=region).Table(table_name)

    def build_placeholder_record(
        self,
        image_name: str,
        image_url: str,
        labels: list[str],
        translations: dict[str, list[str]],
    ) -> dict:
        return {
            "record_id": str(uuid4()),
            "created_at": datetime.now(UTC).isoformat(),
            "image_name": image_name,
            "image_url": image_url,
            "labels": labels,
            "translations": translations,
        }

    def save_record(self, record: dict) -> dict:
        self.table.put_item(Item=record)
        return record

    def get_record(self, record_id: str) -> dict | None:
        response = self.table.get_item(Key={"record_id": record_id})
        return response.get("Item")

    def list_records(self, limit: int = 25) -> list[dict]:
        response = self.table.scan(Limit=limit)
        items = response.get("Items", [])
        return sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)
