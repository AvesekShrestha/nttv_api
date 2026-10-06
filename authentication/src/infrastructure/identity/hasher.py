from argon2 import PasswordHasher as Argon2PasswordHasher

from src.application.shared.hasher_interface import IHasher


class Hasher(IHasher):
    def __init__(self) -> None:
        self._hasher = Argon2PasswordHasher()

    async def hash(self, password: str) -> str:
        return self._hasher.hash(password)

    async def verify(
        self,
        password: str,
        hashed_password: str,
    ) -> bool:
        try:
            return self._hasher.verify(hashed_password, password)
        except Exception:
            return False
