import json
import sqlite3
from datetime import date
from typing import List, Optional
from src.domain.entities.body_metric import BodyMetricEntry
from src.domain.repositories.body_metric_repository import BodyMetricRepository


class SQLiteBodyMetricRepository(BodyMetricRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def save(self, entry: BodyMetricEntry) -> None:
        self._conn.execute(
            """INSERT OR REPLACE INTO body_metrics
               (id, recorded_at, bodyweight, measurements_json, notes)
               VALUES (?, ?, ?, ?, ?)""",
            (
                entry.id,
                entry.recorded_at.isoformat(),
                entry.bodyweight,
                json.dumps(entry.measurements) if entry.measurements else None,
                entry.notes,
            ),
        )
        self._conn.commit()

    def find_by_id(self, entry_id: str) -> Optional[BodyMetricEntry]:
        cursor = self._conn.execute(
            "SELECT * FROM body_metrics WHERE id = ?", (entry_id,)
        )
        row = cursor.fetchone()
        return self._row_to_entry(row) if row else None

    def find_all(self, limit: Optional[int] = None) -> List[BodyMetricEntry]:
        query = "SELECT * FROM body_metrics ORDER BY recorded_at DESC"
        params: list = []
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        cursor = self._conn.execute(query, params)
        return [self._row_to_entry(row) for row in cursor.fetchall()]

    def delete(self, entry_id: str) -> None:
        self._conn.execute("DELETE FROM body_metrics WHERE id = ?", (entry_id,))
        self._conn.commit()

    def _row_to_entry(self, row: sqlite3.Row) -> BodyMetricEntry:
        return BodyMetricEntry(
            id=row["id"],
            recorded_at=date.fromisoformat(row["recorded_at"]),
            bodyweight=row["bodyweight"],
            measurements=json.loads(row["measurements_json"]) if row["measurements_json"] else None,
            notes=row["notes"],
        )
