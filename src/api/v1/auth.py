"""
Auth Api.

Author : Coke
Date   : 2025-03-11
"""

from fastapi import APIRouter, Depends

from src.core.config import auth_settings
from src.core.route import BaseRoute
from src.deps.auth import AuthCrudDep, OAuth2Form, UserDBDep, UserJWTDep
from src.deps.environment import check_debug
from src.schemas.auth import LoginRequest, OAuth2TokenResponse, TokenResponse, UserInfoResponse, UserJWT
from src.schemas.response import Response
from src.services.auth import create_access_token, user_login

router = APIRouter(prefix="/auth", tags=["Auth"], route_class=BaseRoute)


@router.get("/keys/public")
async def get_public_key() -> Response[str]:
    """Obtain the public key for RSA encryption of password."""

    return Response(data=auth_settings.RSA_PUBLIC_KEY.get_secret_value())


@router.post("/login")
async def login(body: LoginRequest, auth: AuthCrudDep) -> Response[TokenResponse]:
    """
    User login endpoint.

    This endpoint validates the user's credentials, decrypts the password,
    checks it against the database, and returns access and refresh tokens upon success.

    Args:
        body (LoginRequest): The login request payload containing username and encrypted password.
        auth (AuthCrudDep): Dependency-injected authentication CRUD logic.

    Returns:
        Response[TokenResponse]: A standardized response containing access and refresh tokens.
    """
    token = await user_login(body.username, body.password, user_crud=auth)
    return Response(data=token)


@router.post("/login/swagger", include_in_schema=False, dependencies=[Depends(check_debug)])
async def login_swagger(form: OAuth2Form, auth: AuthCrudDep) -> OAuth2TokenResponse:
    """
    Authenticate the user through Swagger login and generate an access token.

    This endpoint is intended for development or testing environments
    and is hidden from the public API documentation.

    Args:
        form (OAuth2Form): The login form containing username and password.
        auth (AuthCrudDep): Dependency that provides access to the authentication CRUD logic.

    Returns:
        OAuth2TokenResponse: The generated access token and token type.
    """
    user_info = await auth.get_user_by_username(form.username)
    token = create_access_token(UserJWT(sub=user_info.id, name=user_info.name))  # type: ignore
    return OAuth2TokenResponse(access_token=token, token_type="bearer")


@router.get("/user/info")
async def get_user_info(user: UserDBDep) -> Response[UserInfoResponse]:
    """
    Retrieve the current authenticated user's information.

    This endpoint returns detailed information of the user after validating the token
    and fetching the full record from the database.

    Args:
        user (UserDBDep): Dependency that resolves the current user from the database.

    Returns:
        Response[UserInfoResponse]: A standardized response containing user details.
    """
    return Response(data=UserInfoResponse.model_validate(user))


@router.post("/refresh")
async def refresh_token(user: UserJWTDep) -> Response[str]:
    # TODO: add refresh token.
    return Response(data="123")
