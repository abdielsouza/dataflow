from uuid import uuid4

import pytest
from dataflow_domain import User
from dataflow_infrastructure import InMemoryUserRepository


def test_save_and_get_user_by_id() -> None:
    repository = InMemoryUserRepository()
    user = User(username="abdiel", email="abdiel@example.com", password="hash")

    repository.save(user)

    assert repository.get_by_id(user.id) is user
    assert repository.get_by_email(user.email) is user


def test_get_unknown_user_returns_none() -> None:
    repository = InMemoryUserRepository()

    assert repository.get_by_id(uuid4()) is None
    assert repository.get_by_email("unknown@example.com") is None


def test_cannot_save_different_users_with_same_email() -> None:
    repository = InMemoryUserRepository()
    repository.save(User(username="user_a", email="same@example.com", password="hash-a"))

    duplicate = User(username="user_b", email="same@example.com", password="hash-b")

    with pytest.raises(ValueError, match="User with this email already exists."):
        repository.save(duplicate)