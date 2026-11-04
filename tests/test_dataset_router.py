from pathlib import Path

import pytest
from dataflow_api.main import create_app
from dataflow_api.routers.datasets import _owned_source
from fastapi import HTTPException
from fastapi.testclient import TestClient


def test_dataset_source_is_limited_to_own_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATAFLOW_DATA_DIR", str(tmp_path / "datasets"))
    user_dir = tmp_path / "datasets" / "user-1"
    user_dir.mkdir(parents=True)
    dataset = user_dir / "sample.csv"
    dataset.write_text("name,value\nalpha,1\n", encoding="utf-8")

    assert _owned_source(str(dataset), "user-1") == dataset.resolve()

    with pytest.raises(HTTPException) as exc:
        _owned_source(str(dataset), "user-2")
    assert exc.value.status_code == 403


def test_dataset_source_rejects_unsupported_extension(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATAFLOW_DATA_DIR", str(tmp_path / "datasets"))
    user_dir = tmp_path / "datasets" / "user-1"
    user_dir.mkdir(parents=True)
    dataset = user_dir / "sample.json"
    dataset.write_text("{}", encoding="utf-8")

    with pytest.raises(HTTPException) as exc:
        _owned_source(str(dataset), "user-1")
    assert exc.value.status_code == 422


def test_dataset_upload_cors_allows_filename_header(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATAFLOW_CORS_ORIGINS", "http://localhost:5173")
    client = TestClient(create_app())

    response = client.options(
        "/datasets/upload",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type,x-filename",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "x-filename" in response.headers["access-control-allow-headers"].lower()
