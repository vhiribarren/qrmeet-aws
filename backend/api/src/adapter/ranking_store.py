import boto3
from boto3.dynamodb.conditions import Attr

from port.port import RankingStore


class DynamoRankingStore(RankingStore):

    def __init__(self, dynamo_table_name: str):
        self.table = boto3.resource('dynamodb').Table(dynamo_table_name)

    def add_half_score(self, phone_id: str) -> RankingStore.Score:
        result = self.table.update_item(
            Key={'phone_id': phone_id},
            UpdateExpression="ADD score_half :h, score_full :f",
            ExpressionAttributeValues={":h": 1, ":f": 0},
            ReturnValues="ALL_NEW",
        )
        item = result["Attributes"]
        return RankingStore.Score(phone_id, int(item["score_full"]), int(item["score_half"]))

    def add_full_score(self, phone_id: str) -> RankingStore.Score:
        result = self.table.update_item(
            Key={'phone_id': phone_id},
            UpdateExpression="ADD score_half :h, score_full :f",
            ExpressionAttributeValues={":h": 0, ":f": 1},
            ReturnValues="ALL_NEW",
        )
        item = result["Attributes"]
        return RankingStore.Score(phone_id, int(item["score_full"]), int(item["score_half"]))

    def convert_half_to_full_score(self, phone_id: str) -> RankingStore.Score:
        result = self.table.update_item(
            Key={'phone_id': phone_id},
            UpdateExpression="SET score_half = score_half - :h ADD score_full :f",
            ExpressionAttributeValues={":h": 1, ":f": 1},
            ConditionExpression=Attr("phone_id").exists(),
            ReturnValues="ALL_NEW",
        )
        item = result["Attributes"]
        return RankingStore.Score(phone_id, int(item["score_full"]), int(item["score_half"]))

    def score_for(self, phone_id: str) -> RankingStore.Score:
        result = self.table.get_item(
            Key={'phone_id': phone_id}
        )
        item = result.get("Item")
        if item is None:
            return RankingStore.Score(phone_id)
        return RankingStore.Score(phone_id, int(item["score_full"]), int(item["score_half"]))

    def all_scores(self) -> [RankingStore.Score]:
        result = self.table.scan()
        items = result["Items"]
        return [
            RankingStore.Score(i["phone_id"], int(i["score_full"]), int(i["score_half"]))
            for i in items
        ]
