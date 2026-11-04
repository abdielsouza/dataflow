from pathlib import Path

from .connection import connect_database

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def run_migrations() -> None:
    with connect_database() as conn:
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            conn.commit()

            applied = {
                row[0]
                for row in conn.execute("SELECT version FROM schema_migrations").fetchall()
            }

            for migration_path in sorted(MIGRATIONS_DIR.glob("*.sql")):
                version = migration_path.name

                if version in applied:
                    continue

                sql = migration_path.read_text(encoding="utf-8")

                for stmt in sql.split(";"):
                    stmt = stmt.strip()

                    if stmt:
                        conn.execute(stmt)

                conn.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
                conn.commit()

                applied.add(version)

        except Exception:
            conn.rollback()
            raise