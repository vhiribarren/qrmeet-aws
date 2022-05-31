from datetime import datetime, timezone
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from port.port import CodeStore


class DynamoCodeStore(CodeStore):

    def __init__(self, dynamo_table_name: str):
        self.table = boto3.resource('dynamodb').Table(dynamo_table_name)

    def register_code(self, meet_id: str):
        now = datetime.now(timezone.utc).isoformat()
        try:
            self.table.put_item(
                Item={'meet_id': meet_id, 'creation_date': now},
                ConditionExpression=Attr("meet_id").not_exists(),
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise CodeStore.CodeAlreadyExistException() from e
            raise e

    def set_phone_id(self, meet_id: str, phone_id: str):
        try:
            self.table.update_item(
                Key={'meet_id': meet_id},
                UpdateExpression="SET phone_id = :p",
                ExpressionAttributeValues={":p": phone_id},
                ConditionExpression=Attr("meet_id").exists() and Attr("phone_id").not_exists(),
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise CodeStore.PhoneIdException() from e
            raise e

    def get_phone_id(self, meet_id: str) -> Optional[str]:
        result = self.table.get_item(
            Key={'meet_id': meet_id},
        )
        if "Item" not in result:
            raise CodeStore.CodeNotFoundException()
        return result["Item"].get("phone_id")

    def code_exists(self, meet_id: str) -> bool:
        result = self.table.get_item(
            Key={'meet_id': meet_id},
        )
        return "Item" in result

    def _count_codes(self) -> int:
        result = self.table.scan(Select="COUNT")
        return result["Count"]
