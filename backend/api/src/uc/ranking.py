from dataclasses import dataclass
from dataclasses_json import dataclass_json
from port.port import  RankingStore


@dataclass_json
@dataclass(frozen=True)
class RankingInfo:
    username: str
    score_full: int
    score_half: int


class RankingService:

    class PhoneIdNotFoundException(Exception):
        pass

    def __init__(self, ranking_store: RankingStore):
        self.ranking_store = ranking_store

    def global_ranking(self, max_count: int = 10) -> [RankingInfo]:
        pass

    def user_ranking(self, phone_id: str) -> RankingInfo:
        return self.ranking_store.score_for(phone_id)
