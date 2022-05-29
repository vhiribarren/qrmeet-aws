from dataclasses import dataclass

class CodeStore:

    def register_code(self, meet_id):
        raise NotImplementedError()

    def code_exists(self, meet_id) -> bool:
        raise NotImplementedError()

    def count_codes(self) -> int:
        raise NotImplementedError()

class UserStore:

    def register_user(self, phone_id, meet_id, name):
        raise NotImplementedError()

    def user_exists(self, phone_id) -> bool:
        raise NotImplementedError()

    def update_user_name(self, phone_id, name):
        raise NotImplementedError()

    def get_phone_id(self, meet_id) -> str:
        raise NotImplementedError()


class MeetStore:

    def check_if_already_met(self, from_phone_id, meet_id) -> bool:
        raise NotImplementedError()

    def update_meet_list(self, from_phone_id, meet_id):
        raise NotImplementedError()

    def meet_list_size(self, phone_id) -> int:
        raise NotImplementedError()


class RankingStore:

    @dataclass(frozen=True, kw_only=True)
    class Score:
        phone_id: str
        score: int

    def score_for(self, phone_id) -> int:
        raise NotImplementedError()

    def best_scores(self, size: int = 10) -> [Score]:
        raise NotImplementedError()
