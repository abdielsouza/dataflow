"""Aplicação FastAPI principal para expor os endpoints do Dataflow."""
import os
from contextlib import asynccontextmanager

from dataflow_storage import run_migrations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Dataflow API", version="0.1.0", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            origin.strip()
            for origin in os.getenv(
                "DATAFLOW_CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173,http://10.58.252.165:5173",
            ).split(",")
            if origin.strip()
        ],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Filename"],
    )

    routers = (
        AuthRouter(),
        ExecutionRouter(),
        AnalysisRouter(),
        DatasetRouter(),
    )

    for router in routers:
        router.include_in(app)

    return app

app = create_app()