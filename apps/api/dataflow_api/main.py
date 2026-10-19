"""Aplicação FastAPI principal para expor os endpoints do Dataflow."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .routers import *

from dataflow_storage import run_migrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Dataflow API", version="0.1.0", lifespan=lifespan)

    routers = (
        AuthRouter(),
        ExecutionRouter(),
        AnalysisRouter(),
    )

    for router in routers:
        router.include_in(app)

    return app

app = create_app()