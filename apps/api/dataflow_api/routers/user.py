from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status

from ..dependencies import get_current_user, get_user_service
from ..schemas import UpdateUserRequest, UpdateUserResponse, UserResponse
from ..services import UserService
from dataflow_domain import User
from .base import AbstractRouter

class UserRouter(AbstractRouter):
    """The user CRUD routing logic."""

    prefix = "/users"
    tags = ("users",)

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/me",
            self.get_current,
            methods=["GET"],
            response_model=UserResponse,
        )
        self.router.add_api_route(
            "/me",
            self.update_current,
            methods=["PATCH"],
            response_model=UpdateUserResponse,
        )
        self.router.add_api_route(
            "/me",
            self.delete_current,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
        )
        self.router.add_api_route(
            "/{user_id}",
            self.get_user,
            methods=["GET"],
            response_model=UserResponse,
        )
        self.router.add_api_route(
            "/{user_id}",
            self.update_user,
            methods=["PATCH"],
            response_model=UpdateUserResponse,
        )
        self.router.add_api_route(
            "/{user_id}",
            self.delete_user,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
        )

        # Backward-compatible route kept for existing API consumers.
        self.router.add_api_route(
            "/delete",
            self.delete_legacy,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
        )

    def get_current(
        self,
        current_user: User = Depends(get_current_user),
    ) -> UserResponse:
        return UserResponse.from_domain(current_user)

    def get_user(
        self,
        user_id: UUID,
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
    ) -> UserResponse:
        self._ensure_owner(current_user, user_id)
        user = user_service.get_user(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found.")
        return UserResponse.from_domain(user)

    def update_current(
        self,
        request: UpdateUserRequest,
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
    ) -> UpdateUserResponse:
        return self._update_user(current_user.id, request, user_service)

    def update_user(
        self,
        user_id: UUID,
        request: UpdateUserRequest,
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
    ) -> UpdateUserResponse:
        self._ensure_owner(current_user, user_id)
        return self._update_user(user_id, request, user_service)

    def _update_user(
        self,
        user_id: UUID,
        request: UpdateUserRequest,
        user_service: UserService,
    ) -> UpdateUserResponse:
        try:
            user = user_service.update_user(
                user_id,
                username=request.username,
                email=request.email,
                password=request.password,
            )
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        return UpdateUserResponse.from_domain(user)

    def delete_current(
        self,
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
    ) -> None:
        user_service.delete_user(current_user.id)

    def delete_user(
        self,
        user_id: UUID,
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
    ) -> None:
        self._ensure_owner(current_user, user_id)
        if user_service.get_user(user_id) is None:
            raise HTTPException(status_code=404, detail="User not found.")
        user_service.delete_user(user_id)

    def delete_legacy(
        self,
        user_id: UUID | None = None,
        current_user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
    ) -> None:
        target_id = user_id or current_user.id
        self._ensure_owner(current_user, target_id)
        if user_service.get_user(target_id) is None:
            raise HTTPException(status_code=404, detail="User not found.")
        user_service.delete_user(target_id)

    @staticmethod
    def _ensure_owner(current_user: User, user_id: UUID) -> None:
        if current_user.id != user_id:
            raise HTTPException(status_code=403, detail="Cannot access another user.")

    def include_in(self, app: FastAPI) -> None:
        super().include_in(app)

        alias = APIRouter(prefix="/user", tags=["user"])
        alias.add_api_route(
            "/me",
            self.get_current,
            methods=["GET"],
            response_model=UserResponse,
        )
        alias.add_api_route(
            "/me",
            self.update_current,
            methods=["PATCH"],
            response_model=UpdateUserResponse,
        )
        alias.add_api_route(
            "/me",
            self.delete_current,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
        )
        alias.add_api_route(
            "/{user_id}",
            self.get_user,
            methods=["GET"],
            response_model=UserResponse,
        )
        alias.add_api_route(
            "/{user_id}",
            self.update_user,
            methods=["PATCH"],
            response_model=UpdateUserResponse,
        )
        alias.add_api_route(
            "/{user_id}",
            self.delete_user,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
        )
        alias.add_api_route(
            "/delete",
            self.delete_legacy,
            methods=["DELETE"],
            status_code=status.HTTP_204_NO_CONTENT,
        )
        app.include_router(alias)
