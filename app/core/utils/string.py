import secrets
import string
from base64 import b64encode

CHARACTER_STR = string.digits + string.ascii_lowercase + string.ascii_uppercase


def generate_rstr(length: int) -> str:
    return "".join(secrets.choice(CHARACTER_STR) for _ in range(length))


def base64(s: str) -> str:
    """Encode the string s using Base64."""
    b: bytes = s.encode("utf-8") if isinstance(s, str) else s
    return b64encode(b).decode("ascii")
