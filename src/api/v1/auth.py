"""
Auth Api.

Author : Coke
Date   : 2025-03-11
"""

from fastapi import APIRouter, Depends

from src.core.config import auth_settings
from src.core.route import BaseRoute
from src.deps.auth import (
    AuthCrudDep,
    HeaderUserAgentDep,
    OAuth2Form,
    UserAccessJWTDep,
    UserDBDep,
    UserRefreshDep,
    UserRefreshJWTDep,
    refresh_structure,
)
from src.deps.database import RedisDep
from src.deps.environment import check_debug
from src.schemas.auth import (
    LoginRequest,
    OAuth2TokenResponse,
    TokenResponse,
    UserAccessJWT,
    UserInfoResponse,
)
from src.schemas.response import Response
from src.services.auth import create_access_token, refresh_user_token, user_login
from src.utils.uuid7 import uuid8

router = APIRouter(prefix="/auth", tags=["Auth"], route_class=BaseRoute)


@router.get("/keys/public")
async def get_public_key() -> Response[str]:
    """Obtain the public key for RSA encryption of password."""

    return Response(data=auth_settings.RSA_PUBLIC_KEY.get_secret_value())


@router.post("/login")
async def login(
    body: LoginRequest,
    auth: AuthCrudDep,
    redis: RedisDep,
    user_agent: HeaderUserAgentDep,
) -> Response[TokenResponse]:
    """
    User login endpoint.

    This endpoint validates the user's credentials, decrypts the password,
    checks it against the database, and returns access and refresh tokens upon success.\f

    Args:
        body (LoginRequest): The login request payload containing username and encrypted password.
        auth (AuthCrudDep): Dependency-injected authentication CRUD logic.
        redis (RedisDep): Redis client dependency.
        user_agent (HeaderUserAgentDep): User-Agent request object.

    Returns:
        Response[TokenResponse]: A standardized response containing access and refresh tokens.
    """
    token = await user_login(body.username, body.password, user_crud=auth, redis=redis, user_agent=user_agent)
    return Response(data=token)


@router.post("/logout")
async def logout(auth: UserAccessJWTDep, redis: RedisDep) -> Response[bool]:
    """
    Log out the current user.\f

    Args:
        auth (UserAccessJWTDep): The access token containing the user's identity and metadata.
        redis (RedisDep): Redis client dependency for interacting with the Redis database.

    Returns:
        Response[bool]: A response indicating whether the logout process was successful.
    """
    token = refresh_structure.format(user_id=auth.user_id, jti=auth.jti)
    if await redis.exists(token):
        await redis.delete(token)

    return Response(data=True)


@router.post("/token/refresh")
async def refresh_token(
    jwt_user: UserRefreshJWTDep,
    user: UserRefreshDep,
    redis: RedisDep,
    user_agent: HeaderUserAgentDep,
) -> Response[TokenResponse]:
    """
    Refresh the user's access token using their refresh token.\f

    Args:
        jwt_user (UserRefreshJWTDep): Refresh token user info.
        user (UserRefreshDep): The decoded user data retrieved using the refresh token.
        redis (RedisDep): Redis client dependency for interacting with the Redis database.
        user_agent (HeaderUserAgentDep): The user-agent header from the request, used to validate the request.

    Returns:
        Response[TokenResponse]: A response containing the new access and refresh tokens for the user.

    Raises:
        PermissionDeniedException: If the refresh token is invalid.
        BadRequestException: If the user-agent does not match.
    """
    token = await refresh_user_token(user.id, user.name, jwt_user.jti, redis, user_agent)
    return Response(data=token)


@router.post("/login/swagger", include_in_schema=False, dependencies=[Depends(check_debug)])
async def login_swagger(form: OAuth2Form, auth: AuthCrudDep) -> OAuth2TokenResponse:
    """
    Authenticate the user through Swagger login and generate an access token.

    This endpoint is intended for development or testing environments
    and is hidden from the public API documentation.\f

    Args:
        form (OAuth2Form): The login form containing username and password.
        auth (AuthCrudDep): Dependency that provides access to the authentication CRUD logic.

    Returns:
        OAuth2TokenResponse: The generated access token and token type.
    """
    user_info = await auth.get_user_by_username(form.username)
    token = create_access_token(
        UserAccessJWT.model_validate(
            {
                "sub": user_info.id,
                "name": user_info.name,
                "jti": uuid8(),
            }
        )
    )
    return OAuth2TokenResponse(access_token=token, token_type="bearer")


@router.get("/user/info")
async def get_user_info(user: UserDBDep) -> Response[UserInfoResponse]:
    """
    Retrieve the current authenticated user's information.

    This endpoint returns detailed information of the user after validating the token
    and fetching the full record from the database.\f

    Args:
        user (UserDBDep): Dependency that resolves the current user from the database.

    Returns:
        Response[UserInfoResponse]: A standardized response containing user details.
    """
    return Response(data=UserInfoResponse.model_validate(user))


@router.get("/user/{user_id}/project/{project_id}")
async def get_user_info1(user: UserDBDep) -> Response[UserInfoResponse]: ...  # type: ignore  # TODO: remove.


@router.get("/user/{user_id}", summary="测试结构哦")
async def get_user_info2(user: UserDBDep) -> Response[UserInfoResponse]: ...  # type: ignore  # TODO: remove.
