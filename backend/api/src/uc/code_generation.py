from port.port import CodeStore


class CodeGeneratorService:

    def __init__(self, code_store: CodeStore):
        pass

    def generate_meet_ids(self, count: int = 1) -> [str]:
        pass

    def check_meet_id_validity(self, meet_id:  str) -> bool:
        pass

    @staticmethod
    def _random_meet_id() -> str:
        pass

    @staticmethod
    def _verify_meet_id(id: str) -> bool:
        pass