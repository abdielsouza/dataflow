from uuid import UUID

from dataflow_domain import User

from dataflow_storage.connection import connect_database


class TursoUserRepository:
    def get_by_id(self, user_id: UUID) -> User | None:
        connection = connect_database()

        try:
            row = connection.execute(
                """
                SELECT id, username, email, password
                FROM users
                WHERE id = ?
                """,
                (str(user_id),),
            ).fetchone()

            if row is None:
                return None

            return User(
                id=UUID(row[0]),
                username=row[1],
                email=row[2],
                password=row[3],
            )
        finally:
            connection.close()

    def get_by_email(self, email: str) -> User | None:
        connection = connect_database()

        try:
            row = connection.execute(
                """
                SELECT id, username, email, password
                FROM users
                WHERE email = ?
                """,
                (email.strip(),),
            ).fetchone()

            if row is None:
                return None

            return User(
                id=UUID(row[0]),
                username=row[1],
                email=row[2],
                password=row[3],
            )
        finally:
            connection.close()

    def save(self, user: User) -> None:
        connection = connect_database()

        try:
            connection.execute(
                """
                INSERT INTO users (
                    id, username, email, password
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    username = excluded.username,
                    email = excluded.email,
                    password = excluded.password
                """,
                (
                    str(user.id),
                    user.username,
                    user.email.strip(),
                    user.password,
                ),
            )
            connection.commit()
        finally:
            connection.close()

    def delete(self, user_id: UUID) -> None:
        connection = connect_database()

        try:
            connection.execute(
                """
                DELETE FROM users WHERE id = ?
                """,
                (
                    str(user_id),
                )
            )
            connection.commit()
        finally:
            connection.close()

    def update(self, user: User) -> None:
        connection = connect_database()

        try:
            existing = connection.execute(
                "SELECT id FROM users WHERE email = ? AND id != ?",
                (user.email.strip().casefold(), str(user.id)),
            ).fetchone()
            if existing is not None:
                raise ValueError("User with this email already exists.")

            connection.execute(
                """
                UPDATE users
                SET username = ?, email = ?, password = ?
                WHERE id = ?
                """,
                (
                    user.username,
                    user.email.strip().casefold(),
                    user.password,
                    str(user.id),
                ),
            )
            connection.commit()
        finally:
            connection.close()
