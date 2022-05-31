import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from port.port import MeetStore


class DynamoMeetStore(MeetStore):

    def __init__(self, dynamo_table_name):
        self.table = boto3.resource('dynamodb').Table(dynamo_table_name)

    def check_if_already_met(self, from_phone_id: str, scanned_phone_id: str) -> bool:
        result = self.table.get_item(
            Key={'phone_id': from_phone_id},
        )
        if "Item" not in result:
            raise MeetStore.PhoneIdDoesNotExistException()
        return scanned_phone_id in result["Item"].get("scanned_phone_id_set", set())

    def update_meet_list(self, from_phone_id: str, scanned_phone_id: str):
        try:
            self.table.update_item(
                Key={'phone_id': from_phone_id},
                UpdateExpression="ADD scanned_phone_id_set :p",
                ExpressionAttributeValues={":p": {scanned_phone_id}},
                ConditionExpression=Attr("phone_id").exists(),
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise MeetStore.PhoneIdDoesNotExistException() from e
            raise e

    def meet_list_size(self, phone_id: str) -> int:
        result = self.table.get_item(
            Key={'phone_id': phone_id},
        )
        if "Item" not in result:
            raise MeetStore.PhoneIdDoesNotExistException()
        return len(result["Item"].get("scanned_phone_id_set", []))
