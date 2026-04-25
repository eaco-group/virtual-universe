from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    solana_rpc_url: str
    solana_private_key_base58: str
    fee_min_bps: int
    fee_max_bps: int
    default_fee_bps: int
    fee_accounts_path: str
    sqlite_path: str
    jupiter_quote_url: str
    jupiter_swap_url: str


def load_settings() -> Settings:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    secret = os.getenv("SOLANA_PRIVATE_KEY_BASE58", "")
    if not token or not secret:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and SOLANA_PRIVATE_KEY_BASE58 are required")

    return Settings(
        telegram_bot_token=token,
        solana_rpc_url=os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"),
        solana_private_key_base58=secret,
        fee_min_bps=int(os.getenv("FEE_MIN_BPS", "15")),
        fee_max_bps=int(os.getenv("FEE_MAX_BPS", "75")),
        default_fee_bps=int(os.getenv("DEFAULT_FEE_BPS", "25")),
        fee_accounts_path=os.getenv("FEE_ACCOUNTS_PATH", "fee_accounts.json"),
        sqlite_path=os.getenv("SQLITE_PATH", "eaco_bot.db"),
        jupiter_quote_url=os.getenv("JUPITER_QUOTE_URL", "https://quote-api.jup.ag/v6/quote"),
        jupiter_swap_url=os.getenv("JUPITER_SWAP_URL", "https://quote-api.jup.ag/v6/swap"),
    )
