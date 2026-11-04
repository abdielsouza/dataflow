from uuid import UUID

from dataflow_domain import User
from dataflow_storage import TursoAnalysisRepository
from fastapi import Depends, HTTPException

from ..dependencies import get_analysis_repository, get_current_user
from ..schemas import (
    AnalysisListItem,
    AnalysisRequest,
    SavedAnalysisResponse,
)
from .base import AbstractRouter


class AnalysisRouter(AbstractRouter):
    prefix = "/analyses"
    tags = ("analyses",)

    def _register_routes(self):
        self.router.add_api_route(
            "",
            self.create,
            methods=["POST"],
            response_model=SavedAnalysisResponse,
            status_code=201,
        )

        self.router.add_api_route(
            "",
            self.list_analyses,
            methods=["GET"],
            response_model=list[AnalysisListItem],
        )

        self.router.add_api_route(
            "/{analysis_id}",
            self.get,
            methods=["GET"],
            response_model=SavedAnalysisResponse,
        )

        self.router.add_api_route(
            "/{analysis_id}",
            self.update,
            methods=["PUT"],
            response_model=SavedAnalysisResponse,
        )


    def create(
        self,
        request: AnalysisRequest,
        user: User = Depends(get_current_user),
        repo: TursoAnalysisRepository = Depends(get_analysis_repository),
    ) -> SavedAnalysisResponse:
        try:
            request.to_domain()

        except (ValueError, KeyError, TypeError) as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid analysis definition: {exc}",
            ) from exc

        definition = request.model_dump(mode="json")
        saved = repo.save(owner_id=user.id, definition=definition)

        return SavedAnalysisResponse.model_validate(saved)


    def list_analyses(
        self,
        user: User = Depends(get_current_user),
        repo: TursoAnalysisRepository = Depends(get_analysis_repository),
    ) -> list[AnalysisListItem]:
        analyses = repo.list_by_owner(user.id)

        return [AnalysisListItem.model_validate(analysis) for analysis in analyses]


    def update(
        self,
        analysis_id: UUID,
        request: AnalysisRequest,
        user: User = Depends(get_current_user),
        repo: TursoAnalysisRepository = Depends(get_analysis_repository),
    ) -> SavedAnalysisResponse:
        try:
            request.to_domain()
        except (ValueError, KeyError, TypeError) as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid analysis definition: {exc}",
            ) from exc

        saved = repo.update(
            owner_id=user.id,
            analysis_id=analysis_id,
            definition=request.model_dump(mode="json"),
        )
        if saved is None:
            raise HTTPException(status_code=404, detail="Analysis not found.")

        return SavedAnalysisResponse.model_validate(saved)


    def get(
        self,
        analysis_id: UUID,
        user: User = Depends(get_current_user),
        repo: TursoAnalysisRepository = Depends(get_analysis_repository),
    ) -> SavedAnalysisResponse:
        if (analysis := repo.get_by_id(owner_id=user.id, analysis_id=analysis_id)) is None:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found.",
            )

        else:
            return SavedAnalysisResponse.model_validate(analysis)