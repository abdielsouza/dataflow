"""Upload and preview datasets owned by the authenticated user."""

import os
from pathlib import Path
from urllib.parse import unquote
from uuid import uuid4

import polars as pl
from dataflow_domain import User
from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel

from ..dependencies import get_current_user
from .base import AbstractRouter

MAX_DATASET_BYTES = 20 * 1024 * 1024
ALLOWED_SUFFIXES = {".csv", ".parquet"}


def _data_root() -> Path:
    return Path(os.getenv("DATAFLOW_DATA_DIR", ".dataflow/datasets")).expanduser().resolve()


def _owned_source(source: str, user_id: str) -> Path:
    root = (_data_root() / str(user_id)).resolve()
    path = Path(source).expanduser().resolve()
    try:
        path.relative_to(root)
    except ValueError:
        raise HTTPException(status_code=403, detail="Dataset source is not accessible.") from None
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=422, detail="Only CSV and Parquet datasets are supported.")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Dataset file not found.")
    return path


def _preview(path: Path, limit: int = 20) -> dict:
    try:
        if path.suffix.lower() == ".csv":
            frame = pl.read_csv(path).head(limit)
        else:
            frame = pl.read_parquet(path).head(limit)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Unable to read dataset: {exc}") from exc
    return {
        "columns": [{"name": name, "dtype": str(dtype)} for name, dtype in frame.schema.items()],
        "rows": frame.to_dicts(),
        "preview_row_count": frame.height,
    }


class DatasetPreviewRequest(BaseModel):
    source: str


class DatasetRouter(AbstractRouter):
    prefix = "/datasets"
    tags = ("datasets",)

    def _register_routes(self):
        self.router.add_api_route("/upload", self.upload, methods=["POST"], status_code=201)
        self.router.add_api_route("/preview", self.preview, methods=["POST"])

    async def upload(self, request: Request, user: User = Depends(get_current_user)) -> dict:
        filename = unquote(request.headers.get("x-filename", "").strip())
        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_SUFFIXES:
            raise HTTPException(status_code=422, detail="Choose a .csv or .parquet file.")

        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > MAX_DATASET_BYTES:
                    raise HTTPException(status_code=413, detail="Dataset exceeds the 20 MB upload limit.")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid Content-Length header.") from None

        chunks = bytearray()
        async for chunk in request.stream():
            chunks.extend(chunk)
            if len(chunks) > MAX_DATASET_BYTES:
                raise HTTPException(status_code=413, detail="Dataset exceeds the 20 MB upload limit.")
        content = bytes(chunks)
        if not content:
            raise HTTPException(status_code=422, detail="The uploaded file is empty.")

        user_dir = (_data_root() / str(user.id)).resolve()
        user_dir.mkdir(parents=True, exist_ok=True)
        path = user_dir / f"{uuid4().hex}{suffix}"
        path.write_bytes(content)
        try:
            preview = _preview(path)
        except HTTPException:
            path.unlink(missing_ok=True)
            raise

        return {
            "name": Path(filename).name,
            "source": str(path),
            "size_bytes": len(content),
            **preview,
        }

    def preview(self, request: DatasetPreviewRequest, user: User = Depends(get_current_user)) -> dict:
        path = _owned_source(request.source, str(user.id))
        return {"name": path.name, **_preview(path)}
