import secrets
import string

CHARACTER_STR = string.digits + string.ascii_lowercase + string.ascii_uppercase


def generate_rstr(length: int) -> str:
    return "".join(secrets.choice(CHARACTER_STR) for _ in range(length))
