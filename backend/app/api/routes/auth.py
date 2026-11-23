from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_auth_service, get_current_user
from app.core.exceptions import DuplicateUserError, InactiveUserError, InvalidCredentialsError
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.common import TokenResponse, UserPublic

router = APIRouter(prefix="/auth", tags=["authentication"])


def token_response(user: dict, token: str) -> TokenResponse:
    return TokenResponse(
        access_token=token,
        user=UserPublic(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"],
        ),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, service=Depends(get_auth_service)):
    try:
        user, token = await service.register(payload.name, payload.email, payload.password)
    except DuplicateUserError as exc:
        raise HTTPException(
            status_code=409, detail="An account with this email already exists."
        ) from exc
    return token_response(user, token)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, service=Depends(get_auth_service)):
    try:
        user, token = await service.login(payload.email, payload.password)
    except (InvalidCredentialsError, InactiveUserError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return token_response(user, token)


@router.get("/me", response_model=UserPublic)
async def current_user(user=Depends(get_current_user)):
    return UserPublic(
        id=str(user["_id"]),
        name=user["name"],
        email=user["email"],
        created_at=user["created_at"],
    )
