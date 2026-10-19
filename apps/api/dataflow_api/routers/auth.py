from fastapi import Depends, HTTPException

from ..services import AuthService
from ..security import TokenHandler
from ..schemas import (
    LoginRequest,
    RegisterRequest,
    UserResponse,
    TokenResponse,
)
from .base import AbstractRouter
from ..dependencies import get_auth_service, get_token_handler


class AuthRouter(AbstractRouter):
    prefix = "/auth"
    tags = ("auth",)

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/register",
            self.register,
            methods=["POST"],
            response_model=UserResponse,
        )

        self.router.add_api_route(
            "/login",
            self.login,
            methods=["POST"],
            response_model=TokenResponse,
        )

    def register(
        self,
        request: RegisterRequest,
        service: AuthService = Depends(get_auth_service),
    ) -> UserResponse:
        user = service.register(
            username=request.username,
            email=request.email,
            password=request.password,
        )

        return UserResponse.from_domain(user)

    def login(
        self,
        request: LoginRequest,
        service: AuthService = Depends(get_auth_service),
        token_handler: TokenHandler = Depends(get_token_handler),
    ) -> TokenResponse:
        try:
            user = service.authenticate(
                email=request.email,
                password=request.password,
            )

        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid credentials.") from None

        access_token = token_handler.create_access_token(user.id)

        return TokenResponse(access_token=access_token)