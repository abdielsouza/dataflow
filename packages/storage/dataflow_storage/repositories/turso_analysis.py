import json
from typing import Any, Optional
from uuid import UUID, uuid4

from ..connection import connect_database


class TursoAnalysisRepository:
    def save(self, owner_id: UUID, definition: dict[str, Any]) -> dict[str, Any]:
        analysis_id = uuid4()
        dataset_id = uuid4()

        dataset = definition["dataset"]
        name = definition["name"]

        with connect_database() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO datasets (id, owner_id, name, source)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        str(dataset_id),
                        str(owner_id),
                        dataset["name"],
                        dataset["source"],
                    ),
                )

                conn.execute(
                    """
                    INSERT INTO analyses (id, owner_id, dataset_id, name, definition_json)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        str(analysis_id),
                        str(owner_id),
                        str(dataset_id),
                        name,
                        json.dumps(definition, ensure_ascii=False),
                    ),
                )

                conn.commit()

            except Exception:
                conn.rollback()
                raise

            # finally:
            #     conn.close()

        return self.get_by_id(owner_id, analysis_id) # type: ignore[return-value]
    


    def update(
        self, owner_id: UUID, analysis_id: UUID, definition: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """Atualiza uma análise existente pertencente ao usuário informado."""
        dataset = definition["dataset"]
        name = definition["name"]

        with connect_database() as conn:
            row = conn.execute(
                "SELECT dataset_id FROM analyses WHERE id = ? AND owner_id = ?",
                (str(analysis_id), str(owner_id)),
            ).fetchone()

            if row is None:
                return None

            dataset_id = row[0]
            try:
                conn.execute(
                    "UPDATE datasets SET name = ?, source = ? WHERE id = ? AND owner_id = ?",
                    (dataset["name"], dataset["source"], dataset_id, str(owner_id)),
                )
                conn.execute(
                    """
                    UPDATE analyses
                    SET name = ?, definition_json = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND owner_id = ?
                    """,
                    (name, json.dumps(definition, ensure_ascii=False), str(analysis_id), str(owner_id)),
                )
                conn.commit()
            except Exception:
                conn.rollback()
                raise

        return self.get_by_id(owner_id, analysis_id)

    def get_by_id(self, owner_id: UUID, analysis_id: UUID) -> Optional[dict[str, Any]]:
        with connect_database() as conn:
            row = conn.execute(
                """
                SELECT
                    a.id,
                    a.owner_id,
                    a.dataset_id,
                    a.name,
                    a.definition_json,
                    a.created_at,
                    a.updated_at,
                    d.name,
                    d.source
                FROM analyses AS a
                JOIN datasets AS d ON d.id = a.dataset_id
                WHERE a.id = ? AND a.owner_id = ?                        
                """,
                (str(analysis_id), str(owner_id)),
            ).fetchone()

            return None if row is None else {
                "id": row[0],
                "owner_id": row[1],
                "dataset_id": row[2],
                "name": row[3],
                "definition": json.loads(row[4]),
                "created_at": row[5],
                "updated_at": row[6],
                "dataset": {
                    "name": row[7],
                    "source": row[8],
                },
            }

        return None
    

    def list_by_owner(self, owner_id: UUID) -> list[dict[str, Any]]:
        with connect_database() as conn:
            rows = conn.execute(
                """
                SELECT
                    a.id,
                    a.owner_id,
                    a.dataset_id,
                    a.name,
                    a.definition_json,
                    a.created_at,
                    a.updated_at,
                    d.name,
                    d.source
                FROM analyses AS a
                JOIN datasets AS d ON d.id = a.dataset_id
                WHERE a.owner_id = ?
                ORDER BY a.updated_at DESC, a.created_at DESC       
                """,
                (str(owner_id),),
            ).fetchall()

            return [
                {
                    "id": row[0],
                    "owner_id": row[1],
                    "dataset_id": row[2],
                    "name": row[3],
                    "definition": json.loads(row[4]),
                    "created_at": row[5],
                    "updated_at": row[6],
                    "dataset": {
                        "name": row[7],
                        "source": row[8],
                    },
                }
                for row in rows
            ]

        return []