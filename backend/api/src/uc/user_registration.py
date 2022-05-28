from port.port import UserStore
from uc.code_generation import CodeGeneratorService


class PhoneIdNotFoundException(Exception):
    pass

class InvalidMeetIdException(Exception):
    pass


class UserRegistrationService:

    def __init__(self, meetIdService: CodeGeneratorService, user_store: UserStore):
        pass

    def register_user(self, meet_id: str, name: str) -> str:
        pass

    def update_user(self, phone_id: str, new_name: str):
        pass

    def user_exists(self, phone_id: str) -> bool:
        pass

    def get_phone_id(self, meet_id: str) -> str:
        pass

    @staticmethod
    def _generate_phone_id():
        pass