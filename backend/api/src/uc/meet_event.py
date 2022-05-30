from dataclasses import dataclass
from port.port import MeetStore
from uc.ranking import RankingService
from uc.code_generation import CodeGeneratorService
from uc.user_registration import UserRegistrationService

@dataclass(frozen=True, kw_only=True)
class MeetInfo:
    other_name: str
    is_meet_complete: bool
    count_complete: int
    count_half: int


class MeetService:

    class DuplicateMeetException(Exception):
        pass

    class UnregisteredMeetIdException(Exception):
        pass

    class InvalidMeetIdException(Exception):
        pass

    class UnregisteredPhoneIdException(Exception):
        pass

    def __init__(self, code_service: CodeGeneratorService, ranking_service: RankingService, user_service: UserRegistrationService, meet_store: MeetStore):
        pass

    def meet_other(self, from_phone_id: str, encounter_meet_id: str) -> MeetInfo:
        pass