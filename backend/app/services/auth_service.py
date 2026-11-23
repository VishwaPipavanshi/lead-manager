from bson import ObjectId

from app.core.exceptions import DuplicateUserError, InactiveUserError, InvalidCredentialsError
from app.core.security import create_access_token, hash_password, verify_password


class AuthService:
    def __init__(self, users, settings):
        self.users = users
        self.settings = settings

    async def register(self, name: str, email: str, password: str) -> tuple[dict, str]:
        if await self.users.find_by_email(email):
            raise DuplicateUserError
        user = await self.users.create(name, email, hash_password(password))
        return user, create_access_token(str(user["_id"]), self.settings)

    async def login(self, email: str, password: str) -> tuple[dict, str]:
        user = await self.users.find_by_email(email)
        if not user or not verify_password(password, user["password_hash"]):
            raise InvalidCredentialsError
        if not user["is_active"]:
            raise InactiveUserError
        return user, create_access_token(str(user["_id"]), self.settings)

    async def current_user(self, subject: str) -> dict | None:
        if not ObjectId.is_valid(subject):
            return None
        user = await self.users.find_by_id(ObjectId(subject))
        return user if user and user.get("is_active") else None
