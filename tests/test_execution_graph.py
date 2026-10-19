from uuid import uuid4

import polars as pl
import pytest
from jwt import InvalidTokenError

from dataflow_analytics import PolarsEngine
from dataflow_api.security import PasswordHandler, TokenHandler
from dataflow_domain import Analysis, Artifact, ArtifactType, Dataset, FilterOperation, SortOperation
from dataflow_execution import ExecutionPlanner


def test_execution_planner_orders_graph_stages() -> None:
    analysis = Analysis(name="Análise", dataset=Dataset(name="Dados", source="dados.csv"))
    filter_node = analysis.add_operation(FilterOperation(column="estado", operator="==", value="MG"))
    sort_node = analysis.add_operation(SortOperation(columns=("vendas",), descending=True))
    analysis.graph.add_edge(filter_node, sort_node)

    planned = ExecutionPlanner().plan(analysis.graph)

    assert planned == (filter_node, sort_node)


def test_password_handler_validates_hashes() -> None:
    handler = PasswordHandler()
    password = "senha-secreta"

    hashed = handler.hash(password)

    assert hashed != password
    assert handler.verify(hashed, password) is True
    assert handler.verify(hashed, "outra-senha") is False


def test_token_handler_round_trip() -> None:
    user_id = uuid4()
    secret = "a" * 64
    handler = TokenHandler(secret_key=secret)

    token = handler.create_access_token(user_id)

    assert handler.verify_access_token(token) == user_id
    with pytest.raises(InvalidTokenError):
        handler.verify_access_token("token-invalido")


def test_token_handler_rejects_short_secret() -> None:
    with pytest.raises(ValueError, match="at least 32 bytes"):
        TokenHandler(secret_key="short")


def test_polars_engine_invalid_operator_raises_value_error() -> None:
    engine = PolarsEngine()
    artifact = Artifact(type=ArtifactType.TABLE, data=pl.DataFrame({"estado": ["MG"], "vendas": [100]}))

    with pytest.raises(ValueError, match="Unsupported filter operator: like"):
        engine.execute((artifact,), FilterOperation(column="estado", operator="like", value="MG"))
