from port.port import CodeStore


class CodeGeneratorService:

    def __init__(self, code_store: CodeStore):
        pass

    def generate_meet_urls(self, count: int = 1) -> [str]:
        pass

    def check_meet_id_validity(self, meet_id:  str) -> bool:
        pass

    def check_meet_url_validity(self, meet_url:  str) -> bool:
        pass

    def meet_id_from_url(self, meet_url: str) -> str:
        pass

    @staticmethod
    def _generate_meet_id() -> str:
        pass

    @staticmethod
    def _verify_meet_id(id: str) -> bool:
        pass