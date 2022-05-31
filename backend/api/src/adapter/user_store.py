import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from port.port import UserStore


class DynamoUserStore(UserStore):

    def __init__(self, dynamo_table_name: str):
        self.table = boto3.resource('dynamodb').Table(dynamo_table_name)

    def register_user(self, phone_id: str, meet_id: str, username: str):
        try:
            self.table.put_item(
                Item={
                    'phone_id': phone_id,
                    'meet_id':  meet_id,
                    'username': username,
                },
                ConditionExpression=Attr("phone_id").not_exists()
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise UserStore.PhoneIdAlreadyRegisteredException() from e
            raise e

    def user_exists(self, phone_id: str) -> bool:
        result = self.table.get_item(
            Key={'phone_id': phone_id}
        )
        return "Item" in result

    def update_user_name(self, phone_id: str, username: str):
        try:
            self.table.update_item(
                Key={'phone_id': phone_id},
                UpdateExpression="SET username = :u",
                ExpressionAttributeValues={":u": username},
                ConditionExpression=Attr("phone_id").exists(),
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise UserStore.PhoneIdUnregisteredException() from e
            raise e
