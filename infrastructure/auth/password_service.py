from passlib.context import CryptContext

from domain.value_objects.password import Password


class PasswordService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, password: Password) -> str:
        return self.pwd_context.hash(password.value)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def needs_update(self, hashed_password: str) -> bool:
        return self.pwd_context.needs_update(hashed_password)


password_service = PasswordService()
