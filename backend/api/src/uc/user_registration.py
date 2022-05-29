import uuid

from port.port import UserStore
from uc.code_generation import CodeGeneratorService


class PhoneIdNotFoundException(Exception):
    pass

class InvalidMeetIdException(Exception):
    pass


class UserRegistrationService:

    def __init__(self, code_service: CodeGeneratorService, user_store: UserStore):
        self.code_service = code_service
        self.user_store = user_store

    def register_user(self, meet_id: str, username: str) -> str:
        if not self.code_service.check_meet_id_validity(meet_id):
            raise InvalidMeetIdException("MeetId is invalid")
        if self.user_store.is_meet_id_used(meet_id):
            raise InvalidMeetIdException("MeetId is already registered to someone else")
        phone_id = self._generate_phone_id()
        self.user_store.register_user(phone_id, meet_id, username)
        return phone_id

    def update_user(self, phone_id: str, new_name: str):
        if not self.user_exists(phone_id):
            raise PhoneIdNotFoundException()
        self.user_store.update_user_name(phone_id, new_name)

    def user_exists(self, phone_id: str) -> bool:
        return self.user_store.user_exists(phone_id)

    def get_phone_id(self, meet_id: str) -> str:
        return self.user_store.get_phone_id(meet_id)

    @staticmethod
    def _generate_phone_id() -> str:
        return str(uuid.uuid4())