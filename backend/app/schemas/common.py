from datetime import datetime

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class UserPublic(APIModel):
    id: str
    name: str
    email: str
    created_at: datetime


class TokenResponse(APIModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
