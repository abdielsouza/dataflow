"""Carregamento de datasets em formatos tabulares suportados."""

from pathlib import Path

import polars as pl


class DatasetLoader:
    """Lê arquivos de dados para um DataFrame Polars a partir de um caminho informado."""

    def load(self, source: str) -> pl.DataFrame:
        """Carrega um dataset em .csv ou .parquet e retorna um DataFrame."""
        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")

        match path.suffix.lower():
            case ".csv":
                return pl.read_csv(path)

            case ".parquet":
                return pl.read_parquet(path)

            case suffix:
                raise ValueError(f"Unsupported dataset format: {suffix}")
