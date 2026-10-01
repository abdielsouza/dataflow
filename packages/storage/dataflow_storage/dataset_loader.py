from pathlib import Path

import polars as pl


class DatasetLoader:
    def load(self, source: str) -> pl.DataFrame:
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