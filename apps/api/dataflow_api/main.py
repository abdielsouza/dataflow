"""Aplicação FastAPI principal para expor os endpoints do Dataflow."""

from fastapi import FastAPI

app = FastAPI(title="Dataflow API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Retorna o estado funcional da API para checagem simples de disponibilidade."""
    return {"status": "ok"}