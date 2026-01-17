import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Optional


class TaskRepository:
    """SQLite-backed repository for task inputs and results."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._ensure_schema()

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER UNIQUE,
                    input_hash TEXT UNIQUE NOT NULL,
                    input_payload TEXT NOT NULL,
                    result_hash TEXT,
                    result_payload TEXT,
                    status TEXT NOT NULL,
                    requester TEXT,
                    model TEXT,
                    fee TEXT,
                    chain_id INTEGER,
                    tx_hash TEXT,
                    block_number INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def get_by_input_hash(self, input_hash: str) -> Optional[Dict[str, Any]]:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE input_hash = ?",
                (input_hash,),
            ).fetchone()
            return dict(row) if row else None

    def get_by_task_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        with self._connection() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE task_id = ?",
                (task_id,),
            ).fetchone()
            return dict(row) if row else None

    def insert_prepared(self, input_hash: str, input_payload: str, timestamp: str) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO tasks (input_hash, input_payload, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (input_hash, input_payload, "prepared", timestamp, timestamp),
            )
            conn.commit()

    def update_claim(
        self,
        task_id: int,
        input_hash: str,
        requester: Optional[str],
        model: Optional[str],
        fee: Optional[str],
        chain_id: Optional[int],
        tx_hash: Optional[str],
        block_number: Optional[int],
        timestamp: str,
    ) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                UPDATE tasks
                SET task_id = ?, status = ?, requester = ?, model = ?, fee = ?,
                    chain_id = ?, tx_hash = ?, block_number = ?, updated_at = ?
                WHERE input_hash = ?
                """,
                (
                    task_id,
                    "created",
                    requester,
                    model,
                    fee,
                    chain_id,
                    tx_hash,
                    block_number,
                    timestamp,
                    input_hash,
                ),
            )
            conn.commit()

    def update_result(
        self,
        task_id: int,
        result_hash: str,
        result_payload: str,
        timestamp: str,
    ) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                UPDATE tasks
                SET result_hash = ?, result_payload = ?, status = ?, updated_at = ?
                WHERE task_id = ?
                """,
                (result_hash, result_payload, "completed", timestamp, task_id),
            )
            conn.commit()

    def update_status(
        self,
        task_id: int,
        status: str,
        tx_hash: Optional[str],
        block_number: Optional[int],
        timestamp: str,
    ) -> None:
        with self._connection() as conn:
            conn.execute(
                """
                UPDATE tasks
                SET status = ?, tx_hash = ?, block_number = ?, updated_at = ?
                WHERE task_id = ?
                """,
                (status, tx_hash, block_number, timestamp, task_id),
            )
            conn.commit()
