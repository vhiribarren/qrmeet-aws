import base62
import uuid
import hashlib


from port.port import CodeStore


class CodeGeneratorService:

    MAC_KEY_SECRET = "1e5DD:1(99oZxblurp"

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

    @classmethod
    def _generate_meet_id(cls) -> str:
        meet_id_left = base62.encode(uuid.uuid4().int)[:10]
        h = hashlib.sha256()
        h.update(bytes(meet_id_left+cls.MAC_KEY_SECRET, "utf-8"))
        meet_id_right = base62.encode(int.from_bytes(h.digest(), byteorder='big'))[:5]
        return meet_id_left+meet_id_right

    @classmethod
    def _verify_meet_id(cls, meet_id: str) -> bool:
        meet_id_left = meet_id[:10]
        meet_id_right = meet_id[10:]
        h = hashlib.sha256()
        h.update(bytes(meet_id_left+cls.MAC_KEY_SECRET, "utf-8"))
        computed_meet_id_right = base62.encode(int.from_bytes(h.digest(), byteorder='big'))[:5]
        return meet_id_right == computed_meet_id_right