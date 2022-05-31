from typing import List

from dataclasses import dataclass
from dataclasses_json import dataclass_json

from port.port import RankingStore, UserStore


@dataclass_json
@dataclass(frozen=True)
class RankingInfo:
    username: str
    score_full: int
    score_half: int


class RankingService:

    def __init__(self, ranking_store: RankingStore, user_store: UserStore):
        self.ranking_store = ranking_store
        self.user_store = user_store

    def global_ranking(self, max_count: int = 10) -> List[RankingInfo]:
        all_scores = sorted(self.ranking_store.all_scores(), key=lambda s: s.score_full, reverse=True)
        score_full_threshold = all_scores[max_count-1].score_full
        i = max_count
        for i in range(max_count, len(all_scores)):
            if all_scores[i].score_full != score_full_threshold:
                break
        ranking = []
        for score in all_scores[:i]:
            username = self.user_store.get_username(score.phone_id)
            ranking.append(RankingInfo(username, score.score_full, score.score_half))
        return ranking

    def user_ranking(self, phone_id: str) -> RankingInfo:
        username = self.user_store.get_username(phone_id)
        score = self.ranking_store.score_for(phone_id)
        return RankingInfo(username, score.score_full, score.score_half)
