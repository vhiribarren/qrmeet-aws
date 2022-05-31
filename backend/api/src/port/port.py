from dataclasses import dataclass
from typing import Optional


class CodeStore:

    class PhoneIdException(Exception):
        pass

    class CodeAlreadyExistException(Exception):
        pass

    class CodeNotFoundException(Exception):
        pass

    def register_code(self, meet_id: str):
        raise NotImplementedError()

    def code_exists(self, meet_id: str) -> bool:
        raise NotImplementedError()

    def _count_codes(self) -> int:
        """For test purpose"""
        raise NotImplementedError()

    def set_phone_id(self, meet_id: str, phone_id: str):
        raise NotImplementedError()

    def get_phone_id(self, meet_id: str) -> Optional[str]:
        raise NotImplementedError()


class UserStore:

    class PhoneIdAlreadyRegisteredException(Exception):
        pass

    class PhoneIdUnregisteredException(Exception):
        pass

    def register_user(self, phone_id: str, meet_id: str, username: str):
        raise NotImplementedError()

    def user_exists(self, phone_id: str) -> bool:
        raise NotImplementedError()

    def update_user_name(self, phone_id: str, username: str):
        raise NotImplementedError()


class MeetStore:

    class AlreadyMetException(Exception):
        pass

    class PhoneIdDoesNotExistException(Exception):
        pass

    def check_if_already_met(self, from_phone_id: str, scanned_phone_id: str) -> bool:
        raise NotImplementedError()

    def update_meet_list(self, from_phone_id: str, meet_id: str):
        raise NotImplementedError()

    def meet_list_size(self, phone_id: str) -> int:
        raise NotImplementedError()


class RankingStore:

    @dataclass(frozen=True)
    class Score:
        phone_id: str
        score_full: int
        score_half: int

    def add_half_score(self, phone_id: str) -> Score:
        raise NotImplementedError()

    def add_full_score(self, phone_id: str) -> Score:
        raise NotImplementedError()

    def convert_half_to_full_score(self, phone_id: str) -> Score:
        raise NotImplementedError()

    def score_for(self, phone_id: str) -> Optional[Score]:
        raise NotImplementedError()

    def best_scores(self, size: int = 10) -> [Score]:
        raise NotImplementedError()
