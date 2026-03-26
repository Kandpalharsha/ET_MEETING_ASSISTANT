import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "audit.db"


class AuditLogger:
    def __init__(self):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id             TEXT PRIMARY KEY,
                timestamp      TEXT NOT NULL,
                agent          TEXT NOT NULL,
                action         TEXT NOT NULL,
                input_summary  TEXT,
                output_summary TEXT,
                reasoning      TEXT,
                status         TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save(self, entry: dict):
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            """INSERT OR IGNORE INTO audit_log
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                entry["id"],
                entry["timestamp"],
                entry["agent"],
                entry["action"],
                entry["input_summary"],
                entry["output_summary"],
                entry["reasoning"],
                entry["status"],
            ),
        )
        conn.commit()
        conn.close()

    def get_all(self) -> list[dict]:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT * FROM audit_log ORDER BY timestamp ASC"
        ).fetchall()
        conn.close()
        keys = [
            "id", "timestamp", "agent", "action",
            "input_summary", "output_summary", "reasoning", "status",
        ]
        return [dict(zip(keys, r)) for r in rows]

    def clear(self):
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM audit_log")
        conn.commit()
        conn.close()
