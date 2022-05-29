import base62
import uuid
import hashlib
from string import Template


from port.port import CodeStore


class CodeGeneratorService:

    _MAC_KEY_SECRET = "1e5DD:1(99oZxblurp"

    def __init__(self, meet_url_prefix: str, code_store: CodeStore):
        self.code_store = code_store
        self.meet_url_prefix = meet_url_prefix
        if not self.meet_url_prefix.endswith("/"):
            self.meet_url_prefix += "/"

    def generate_meet_urls(self, count: int = 1) -> [str]:
        urls = []
        for _ in range(count):
            meet_id = self._generate_meet_id()
            self.code_store.register_code(meet_id)
            meet_url = self.meet_url_prefix + meet_id
            urls.append(meet_url)
        return urls

    def check_meet_id_validity(self, meet_id:  str) -> bool:
        mac_condition = self._verify_meet_id(meet_id)
        registered_condition = self.code_store.code_exists(meet_id)
        return mac_condition and registered_condition

    def check_meet_url_validity(self, meet_url:  str) -> bool:
        meet_id = self.meet_id_from_url(meet_url)
        return self._verify_meet_id(meet_id)

    def meet_id_from_url(self, meet_url: str) -> str:
        slash_index = meet_url.rfind("/")
        return meet_url[slash_index+1:]

    @classmethod
    def _generate_meet_id(cls) -> str:
        meet_id_left = base62.encode(uuid.uuid4().int)[:10]
        h = hashlib.sha256()
        h.update(bytes(meet_id_left + cls._MAC_KEY_SECRET, "utf-8"))
        meet_id_right = base62.encode(int.from_bytes(h.digest(), byteorder='big'))[:5]
        return meet_id_left+meet_id_right

    @classmethod
    def _verify_meet_id(cls, meet_id: str) -> bool:
        meet_id_left = meet_id[:10]
        meet_id_right = meet_id[10:]
        h = hashlib.sha256()
        h.update(bytes(meet_id_left + cls._MAC_KEY_SECRET, "utf-8"))
        computed_meet_id_right = base62.encode(int.from_bytes(h.digest(), byteorder='big'))[:5]
        return meet_id_right == computed_meet_id_right