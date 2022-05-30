import boto3
from datetime import datetime, timezone
from port.port import CodeStore
from typing import Optional


class DynamoCodeStore(CodeStore):

    def __init__(self, dynamo_table_name):
        self.table_name = dynamo_table_name
        self.client = boto3.client("dynamodb")

    def register_code(self, meet_id):
        now = datetime.now(timezone.utc).isoformat()
        self.client.put_item(
            TableName=self.table_name,
            Item={'meet_id': {'S': meet_id}, 'creation_date': {'S': now}})

    def set_phone_id(self, meet_id, phone_id):
        if not self.code_exists(meet_id):
            raise CodeStore.CodeDoesNotExistException()
        self.client.put_item(
            TableName=self.table_name,
            Item={'meet_id': {'S': meet_id}, 'phone_id': {'S': phone_id}})

    def get_phone_id(self, meet_id) -> Optional[str]:
        result = self.client.get_item(
            TableName=self.table_name,
            Key={'meet_id': {'S': meet_id}}
        )
        return result["Item"].get("phone_id")

    def code_exists(self, meet_id) -> bool:
        result = self.client.get_item(
            TableName=self.table_name,
            Key={'meet_id': {'S': meet_id}}
        )
        return "Item" in result

    def count_codes(self) -> int:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(self.table_name)
        result = table.scan()
        return result["Count"]