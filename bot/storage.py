from __future__ import annotations

import secrets
import sqlite3
from datetime import UTC, datetime
from pathlib import Path


class Storage:
    def __init__(self, db_path: str, default_fee_bps: int) -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._default_fee_bps = default_fee_bps
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                fee_bps INTEGER NOT NULL,
                language TEXT NOT NULL DEFAULT 'en',
                referral_code TEXT UNIQUE,
                invited_by INTEGER,
                wallet_address TEXT,
                wallet_verified INTEGER NOT NULL DEFAULT 0,
                volunteer_status TEXT NOT NULL DEFAULT 'none',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inviter_id INTEGER NOT NULL,
                invitee_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(inviter_id, invitee_id)
            );

            CREATE TABLE IF NOT EXISTS wallet_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                wallet_address TEXT NOT NULL,
                send_amount INTEGER NOT NULL,
                return_amount INTEGER NOT NULL,
                status TEXT NOT NULL,
                tx_hash TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS trade_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                input_mint TEXT NOT NULL,
                output_mint TEXT NOT NULL,
                amount_atomic INTEGER NOT NULL,
                fee_bps INTEGER NOT NULL,
                slippage_bps INTEGER NOT NULL,
                status TEXT NOT NULL,
                tx_hash TEXT,
                error TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        self._conn.commit()

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()

    def ensure_user(self, telegram_id: int, username: str | None = None) -> sqlite3.Row:
        now = self._now()
        code = f"e{secrets.token_hex(3)}"
        self._conn.execute(
            """
            INSERT OR IGNORE INTO users(
                telegram_id, username, fee_bps, language, referral_code, created_at, updated_at
            ) VALUES(?, ?, ?, 'en', ?, ?, ?)
            """,
            (telegram_id, username, self._default_fee_bps, code, now, now),
        )
        if username:
            self._conn.execute(
                "UPDATE users SET username = ?, updated_at = ? WHERE telegram_id = ?",
                (username, now, telegram_id),
            )
        self._conn.commit()
        row = self._conn.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()
        if row is None:
            raise RuntimeError("failed to initialize user")
        return row

    def get_user(self, telegram_id: int) -> sqlite3.Row:
        row = self._conn.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)).fetchone()
        if row is None:
            return self.ensure_user(telegram_id)
        return row

    def set_language(self, telegram_id: int, language: str) -> None:
        self.ensure_user(telegram_id)
        self._conn.execute(
            "UPDATE users SET language = ?, updated_at = ? WHERE telegram_id = ?",
            (language, self._now(), telegram_id),
        )
        self._conn.commit()

    def get_fee_bps(self, telegram_id: int) -> int:
        user = self.get_user(telegram_id)
        return int(user["fee_bps"])

    def set_fee_bps(self, telegram_id: int, fee_bps: int) -> None:
        self.ensure_user(telegram_id)
        self._conn.execute(
            "UPDATE users SET fee_bps = ?, updated_at = ? WHERE telegram_id = ?",
            (fee_bps, self._now(), telegram_id),
        )
        self._conn.commit()

    def bind_referral(self, invitee_id: int, code: str) -> bool:
        invitee = self.get_user(invitee_id)
        if invitee["invited_by"] is not None:
            return False

        inviter = self._conn.execute("SELECT telegram_id FROM users WHERE referral_code = ?", (code,)).fetchone()
        if inviter is None:
            return False
        inviter_id = int(inviter["telegram_id"])
        if inviter_id == invitee_id:
            return False

        now = self._now()
        self._conn.execute(
            "UPDATE users SET invited_by = ?, updated_at = ? WHERE telegram_id = ?",
            (inviter_id, now, invitee_id),
        )
        self._conn.execute(
            "INSERT OR IGNORE INTO referrals(inviter_id, invitee_id, created_at) VALUES(?, ?, ?)",
            (inviter_id, invitee_id, now),
        )
        self._conn.commit()
        return True

    def referral_stats(self, telegram_id: int) -> tuple[str, int]:
        user = self.get_user(telegram_id)
        code = str(user["referral_code"])
        count_row = self._conn.execute(
            "SELECT COUNT(*) AS c FROM referrals WHERE inviter_id = ?", (telegram_id,)
        ).fetchone()
        return code, int(count_row["c"] if count_row else 0)

    def create_wallet_verification(self, telegram_id: int, wallet_address: str) -> sqlite3.Row:
        now = self._now()
        send_amount = secrets.randbelow(1001) + 2000
        return_amount = send_amount // 2
        self._conn.execute(
            "UPDATE wallet_verifications SET status = 'expired', updated_at = ? WHERE telegram_id = ? AND status = 'pending'",
            (now, telegram_id),
        )
        cur = self._conn.execute(
            """
            INSERT INTO wallet_verifications(
                telegram_id, wallet_address, send_amount, return_amount, status, created_at, updated_at
            ) VALUES(?, ?, ?, ?, 'pending', ?, ?)
            """,
            (telegram_id, wallet_address, send_amount, return_amount, now, now),
        )
        self._conn.commit()
        row = self._conn.execute(
            "SELECT * FROM wallet_verifications WHERE id = ?", (cur.lastrowid,)
        ).fetchone()
        if row is None:
            raise RuntimeError("failed to create verification")
        return row

    def submit_wallet_verification(self, telegram_id: int, verify_id: int, tx_hash: str) -> bool:
        row = self._conn.execute(
            "SELECT * FROM wallet_verifications WHERE id = ? AND telegram_id = ? AND status = 'pending'",
            (verify_id, telegram_id),
        ).fetchone()
        if row is None:
            return False

        now = self._now()
        self._conn.execute(
            "UPDATE wallet_verifications SET status = 'submitted', tx_hash = ?, updated_at = ? WHERE id = ?",
            (tx_hash, now, verify_id),
        )
        self._conn.commit()
        return True

    def approve_wallet_verification(self, verify_id: int) -> bool:
        row = self._conn.execute(
            "SELECT telegram_id, wallet_address FROM wallet_verifications WHERE id = ? AND status = 'submitted'",
            (verify_id,),
        ).fetchone()
        if row is None:
            return False

        now = self._now()
        self._conn.execute(
            "UPDATE wallet_verifications SET status = 'approved', updated_at = ? WHERE id = ?",
            (now, verify_id),
        )
        self._conn.execute(
            "UPDATE users SET wallet_address = ?, wallet_verified = 1, updated_at = ? WHERE telegram_id = ?",
            (row["wallet_address"], now, int(row["telegram_id"])),
        )
        self._conn.commit()
        return True

    def log_trade(
        self,
        telegram_id: int,
        input_mint: str,
        output_mint: str,
        amount_atomic: int,
        fee_bps: int,
        slippage_bps: int,
        status: str,
        tx_hash: str | None = None,
        error: str | None = None,
    ) -> None:
        self._conn.execute(
            """
            INSERT INTO trade_logs(
                telegram_id, input_mint, output_mint, amount_atomic, fee_bps, slippage_bps,
                status, tx_hash, error, created_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (telegram_id, input_mint, output_mint, amount_atomic, fee_bps, slippage_bps, status, tx_hash, error, self._now()),
        )
        self._conn.commit()

    def set_volunteer_status(self, telegram_id: int, status: str) -> None:
        self.ensure_user(telegram_id)
        self._conn.execute(
            "UPDATE users SET volunteer_status = ?, updated_at = ? WHERE telegram_id = ?",
            (status, self._now(), telegram_id),
        )
        self._conn.commit()

    def global_stats(self) -> dict[str, int]:
        u = self._conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()
        r = self._conn.execute("SELECT COUNT(*) AS c FROM referrals").fetchone()
        t = self._conn.execute("SELECT COUNT(*) AS c FROM trade_logs WHERE status = 'success'").fetchone()
        v = self._conn.execute("SELECT COUNT(*) AS c FROM users WHERE wallet_verified = 1").fetchone()
        return {
            "users": int(u["c"] if u else 0),
            "referrals": int(r["c"] if r else 0),
            "successful_swaps": int(t["c"] if t else 0),
            "verified_wallets": int(v["c"] if v else 0),
        }
