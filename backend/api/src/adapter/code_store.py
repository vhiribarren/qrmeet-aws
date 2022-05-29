import boto3
from datetime import datetime, timezone
from port.port import CodeStore


class DynamoCodeStore(CodeStore):

    def __init__(self, dynamo_table_name):
        self.table_name = dynamo_table_name
        self.client = boto3.client("dynamodb")

    def register_code(self, meet_id):
        now = datetime.now(timezone.utc).isoformat()
        self.client.put_item(
            TableName=self.table_name,
            Item={'meet_id': {'S': meet_id}, 'creation_date': {'S': now}})

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