from pathlib import Path

import pytest
from fastapi import HTTPException

from dataflow_api.routers.datasets import _owned_source


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
