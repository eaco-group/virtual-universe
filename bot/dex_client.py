from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import aiohttp
import base58
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solders.keypair import Keypair
from solders.message import to_bytes_versioned
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction import VersionedTransaction


class DexClient:
    def __init__(
        self,
        rpc_url: str,
        private_key_base58: str,
        quote_url: str,
        swap_url: str,
        fee_accounts_path: str,
    ) -> None:
        self._rpc = Client(rpc_url)
        secret = base58.b58decode(private_key_base58)
        if len(secret) == 64:
            self._keypair = Keypair.from_bytes(secret)
        elif len(secret) == 32:
            self._keypair = Keypair.from_seed(secret)
        else:
            raise ValueError("SOLANA_PRIVATE_KEY_BASE58 must decode to 32 or 64 bytes")
        self._quote_url = quote_url
        self._swap_url = swap_url
        self._fee_accounts_path = fee_accounts_path
        self._fee_accounts = self._load_fee_accounts()

    @property
    def public_key(self) -> str:
        return str(self._keypair.pubkey())

    def _load_fee_accounts(self) -> dict[str, str]:
        p = Path(self._fee_accounts_path)
        if not p.exists():
            return {}
        with p.open("r", encoding="utf-8") as f:
            data: Any = json.load(f)
        if not isinstance(data, dict):
            return {}
        return {str(k): str(v) for k, v in data.items()}

    async def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount_atomic: int,
        slippage_bps: int,
        fee_bps: int,
    ) -> dict[str, Any]:
        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount_atomic),
            "slippageBps": str(slippage_bps),
            "restrictIntermediateTokens": "true",
        }
        if fee_bps > 0:
            params["platformFeeBps"] = str(fee_bps)

        async with aiohttp.ClientSession() as session:
            async with session.get(self._quote_url, params=params, timeout=20) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def swap(
        self,
        quote_response: dict[str, Any],
        output_mint: str,
    ) -> str:
        payload: dict[str, Any] = {
            "quoteResponse": quote_response,
            "userPublicKey": self.public_key,
            "wrapAndUnwrapSol": True,
            "dynamicComputeUnitLimit": True,
            "prioritizationFeeLamports": "auto",
        }

        fee_account = self._fee_accounts.get(output_mint)
        if fee_account:
            payload["feeAccount"] = fee_account

        async with aiohttp.ClientSession() as session:
            async with session.post(self._swap_url, json=payload, timeout=30) as resp:
                resp.raise_for_status()
                data = await resp.json()

        swap_tx = data.get("swapTransaction")
        if not swap_tx:
            raise RuntimeError(f"Jupiter did not return swapTransaction: {data}")

        raw_tx = VersionedTransaction.from_bytes(base64.b64decode(swap_tx))
        sig = self._keypair.sign_message(to_bytes_versioned(raw_tx.message))
        signed_tx = VersionedTransaction.populate(raw_tx.message, [sig])
        tx_sig = self._rpc.send_raw_transaction(
            bytes(signed_tx), opts=TxOpts(skip_preflight=False, preflight_commitment="confirmed")
        )
        return str(tx_sig.value)

    def tx_exists(self, tx_hash: str) -> bool:
        sig = Signature.from_string(tx_hash)
        result = self._rpc.get_signature_statuses([sig], search_transaction_history=True)
        val = result.value[0]
        return val is not None


def to_atomic(amount_ui: float, decimals: int) -> int:
    if amount_ui <= 0:
        raise ValueError("amount must be > 0")
    return int(amount_ui * (10**decimals))


def parse_mint_and_decimals(mint_arg: str) -> tuple[str, int]:
    if ":" not in mint_arg:
        raise ValueError("Mint format must be <mint_address>:<decimals>")
    mint, decimals = mint_arg.split(":", 1)
    _ = Pubkey.from_string(mint)
    d = int(decimals)
    if d < 0 or d > 12:
        raise ValueError("decimals out of range (0-12)")
    return mint, d
