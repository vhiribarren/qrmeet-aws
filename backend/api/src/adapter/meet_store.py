import boto3
from port.port import MeetStore


class DynamoMeetStore(MeetStore):

    def __init__(self, dynamo_table_name):
        self.table_name = dynamo_table_name
        self.client = boto3.client("dynamodb")