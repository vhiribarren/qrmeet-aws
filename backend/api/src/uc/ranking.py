from dataclasses import dataclass
from port.port import  RankingStore

@dataclass(frozen=True)
class RankingInfo:
    name: str
    count_full: int
    count_half: int




class RankingService:

    class PhoneIdNotFoundException(Exception):
        pass

    def __init__(self, ranking_store: RankingStore):
        pass

    def global_ranking(self, max: int = 10) -> [RankingInfo]:
        pass

    def user_ranking(self, phone_id: str) -> RankingInfo:
        pass
