from dataclasses import dataclass
from dataclasses_json import dataclass_json
from port.port import MeetStore, RankingStore, CodeStore
from uc.ranking import RankingService
from uc.code_generation import CodeGeneratorService
from uc.user_registration import UserRegistrationService

@dataclass_json
@dataclass(frozen=True)
class MeetInfo:
    is_meet_complete: bool
    score_full: int
    score_half: int


class MeetService:

    class DuplicateMeetException(Exception):
        pass

    class UnregisteredMeetIdException(Exception):
        pass

    class InvalidMeetIdException(Exception):
        pass

    class UnregisteredPhoneIdException(Exception):
        pass

    def __init__(self, code_service: CodeGeneratorService, code_store: CodeStore, user_service: UserRegistrationService, meet_store: MeetStore, ranking_store: RankingStore):
        self.code_service = code_service
        self.code_store = code_store
        self.user_service = user_service
        self.meet_store = meet_store
        self.ranking_store = ranking_store

    def meet_other(self, from_phone_id: str, encounter_meet_id: str) -> MeetInfo:
        try:
            scanned_phone_id = self.code_store.get_phone_id(encounter_meet_id)
        except CodeStore.CodeNotFoundException as e:
            raise self.UnregisteredMeetIdException() from e
        try:
            if self.meet_store.check_if_already_met(from_phone_id, scanned_phone_id):
                raise self.DuplicateMeetException()
        except MeetStore.PhoneIdDoesNotExistException as e:
            raise self.UnregisteredPhoneIdException() from e
        self.meet_store.update_meet_list(from_phone_id, scanned_phone_id)
        if is_mutual_meet := self.meet_store.check_if_already_met(scanned_phone_id, from_phone_id):
            score = self.ranking_store.add_full_score(from_phone_id)
            self.ranking_store.convert_half_to_full_score(scanned_phone_id)
        else:
            score = self.ranking_store.add_half_score(from_phone_id)
        return MeetInfo(is_mutual_meet, score.score_full, score.score_half)
