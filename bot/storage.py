from __future__ import annotations

import sqlite3
from pathlib import Path


class Storage:
    def __init__(self, db_path: str, default_fee_bps: int) -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._default_fee_bps = default_fee_bps
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                fee_bps INTEGER NOT NULL,
                language TEXT DEFAULT 'en'
            )
            """
        )
        self._conn.commit()

    def ensure_user(self, telegram_id: int) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO users(telegram_id, fee_bps) VALUES(?, ?)",
            (telegram_id, self._default_fee_bps),
        )
        self._conn.commit()

    def get_fee_bps(self, telegram_id: int) -> int:
        self.ensure_user(telegram_id)
        row = self._conn.execute(
            "SELECT fee_bps FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        if not row:
            return self._default_fee_bps
        return int(row[0])

    def set_fee_bps(self, telegram_id: int, fee_bps: int) -> None:
        self.ensure_user(telegram_id)
        self._conn.execute(
            "UPDATE users SET fee_bps = ? WHERE telegram_id = ?", (fee_bps, telegram_id)
        )
        self._conn.commit()
