import boto3
from port.port import UserStore


class DynamoUserStore(UserStore):

    def __init__(self, dynamo_table_name):
        self.table_name = dynamo_table_name
        self.client = boto3.client("dynamodb")

    def register_user(self, phone_id, meet_id, username):
        self.client.put_item(
            TableName=self.table_name,
            Item={
                'phone_id': {'S': phone_id},
                'meet_id':  {'S': meet_id},
                'username': {'S': username}
            }
        )

    def user_exists(self, phone_id) -> bool:
        result = self.client.get_item(
            TableName=self.table_name,
            Key={'phone_id': {'S': phone_id}}
        )
        return "Item" in result

    def update_user_name(self, phone_id, username):
        self.client.put_item(
            TableName=self.table_name,
            Item={
                'phone_id': {'S': phone_id},
                'username': {'S': username}
            }
        )