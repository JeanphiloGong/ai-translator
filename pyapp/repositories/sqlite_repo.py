import sqlite3
from contextlib import contextmanager
from pathlib import Path

from pyapp.models.schemas import TranslationResponse


class TranslationRepository:
    """SQLite-backed repository for storing translation results."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self._ensure_schema()

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _ensure_schema(self) -> None:
        """Create table if it does not exist."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS translations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chinese TEXT NOT NULL,
                    english TEXT NOT NULL,
                    english_grammar TEXT,
                    japanese TEXT,
                    hiragana TEXT,
                    japanese_grammar TEXT,
                    timestamp TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def save(self, result: TranslationResponse) -> None:
        """Persist a translation result to the database."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO translations
                (chinese, english, english_grammar, japanese, hiragana, japanese_grammar, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.original_text,
                    result.translated_text,
                    result.english_grammar,
                    result.japanese_text,
                    result.hiragana_pronunciation,
                    result.japanese_grammar,
                    result.timestamp.isoformat(),
                ),
            )
            conn.commit()

