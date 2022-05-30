from dataclasses import dataclass
from typing import Optional


class CodeStore:

    class CodeDoesNotExistException(Exception):
        pass

    def register_code(self, meet_id: str):
        raise NotImplementedError()

    def code_exists(self, meet_id: str) -> bool:
        raise NotImplementedError()

    def count_codes(self) -> int:
        raise NotImplementedError()

    def set_phone_id(self, meet_id: str, phone_id: str):
        raise NotImplementedError()

    def get_phone_id(self, meet_id: str) -> Optional[str]:
        raise NotImplementedError()


class UserStore:

    def register_user(self, phone_id: str, meet_id: str, username: str):
        raise NotImplementedError()

    def user_exists(self, phone_id: str) -> bool:
        raise NotImplementedError()

    def update_user_name(self, phone_id: str, username: str):
        raise NotImplementedError()


class MeetStore:

    def check_if_already_met(self, from_phone_id: str, meet_id: str) -> bool:
        raise NotImplementedError()

    def update_meet_list(self, from_phone_id: str, meet_id: str):
        raise NotImplementedError()

    def meet_list_size(self, phone_id: str) -> int:
        raise NotImplementedError()


class RankingStore:

    @dataclass(frozen=True)
    class Score:
        phone_id: str
        score: int

    def increase_rank(self, phone_id_left: str, phone_id_right: str):
        raise NotImplementedError()

    def score_for(self, phone_id: str) -> int:
        raise NotImplementedError()

    def best_scores(self, size: int = 10) -> [Score]:
        raise NotImplementedError()
