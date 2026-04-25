from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from config import load_settings
from dex_client import DexClient, parse_mint_and_decimals, to_atomic
from storage import Storage

logging.basicConfig(level=logging.INFO)


settings = load_settings()
storage = Storage(settings.sqlite_path, settings.default_fee_bps)
dex = DexClient(
    rpc_url=settings.solana_rpc_url,
    private_key_base58=settings.solana_private_key_base58,
    quote_url=settings.jupiter_quote_url,
    swap_url=settings.jupiter_swap_url,
    fee_accounts_path=settings.fee_accounts_path,
)

bot = Bot(settings.telegram_bot_token)
dp = Dispatcher()


HELP = (
    "EACO DEX Bot commands:\n"
    "/start - register user\n"
    "/help - show help\n"
    "/wallet - show bot wallet pubkey\n"
    "/fee - show your fee bps\n"
    "/setfee <15-75> - set your fee bps\n"
    "/quote <inputMint:decimals> <outputMint:decimals> <amount> [slippageBps]\n"
    "/swap <inputMint:decimals> <outputMint:decimals> <amount> [slippageBps]\n\n"
    "Example:\n"
    "/quote So11111111111111111111111111111111111111112:9 DqfoyZH96RnvZusSp3Cdncjpyp3C74ZmJzGhjmHnDHRH:6 0.5 100"
)


@dp.message(Command("start"))
async def start(message: Message) -> None:
    user_id = int(message.from_user.id)
    storage.ensure_user(user_id)
    await message.answer(
        "Welcome to EACO DEX Bot.\n"
        "Supports Solana token swaps via Jupiter aggregator.\n"
        f"Fee range: {settings.fee_min_bps/100:.2f}% - {settings.fee_max_bps/100:.2f}%"
    )


@dp.message(Command("help"))
async def help_cmd(message: Message) -> None:
    await message.answer(HELP)


@dp.message(Command("wallet"))
async def wallet_cmd(message: Message) -> None:
    await message.answer(f"Bot wallet: `{dex.public_key}`", parse_mode="Markdown")


@dp.message(Command("fee"))
async def fee_cmd(message: Message) -> None:
    user_id = int(message.from_user.id)
    fee_bps = storage.get_fee_bps(user_id)
    await message.answer(f"Your fee: {fee_bps} bps ({fee_bps/100:.2f}%)")


@dp.message(Command("setfee"))
async def set_fee_cmd(message: Message) -> None:
    user_id = int(message.from_user.id)
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Usage: /setfee <15-75>")
        return
    try:
        fee_bps = int(parts[1])
    except ValueError:
        await message.answer("fee must be integer bps")
        return

    if fee_bps < settings.fee_min_bps or fee_bps > settings.fee_max_bps:
        await message.answer(f"fee bps must be between {settings.fee_min_bps} and {settings.fee_max_bps}")
        return

    storage.set_fee_bps(user_id, fee_bps)
    await message.answer(f"Fee updated: {fee_bps} bps ({fee_bps/100:.2f}%)")


async def _quote_or_swap(message: Message, execute: bool) -> None:
    user_id = int(message.from_user.id)
    storage.ensure_user(user_id)

    parts = message.text.split()
    if len(parts) < 4:
        await message.answer("Usage: /quote|/swap <inputMint:decimals> <outputMint:decimals> <amount> [slippageBps]")
        return

    try:
        input_mint, input_decimals = parse_mint_and_decimals(parts[1])
        output_mint, _output_decimals = parse_mint_and_decimals(parts[2])
        amount = float(parts[3])
        slippage = int(parts[4]) if len(parts) > 4 else 100
        amount_atomic = to_atomic(amount, input_decimals)
        fee_bps = storage.get_fee_bps(user_id)

        quote = await dex.get_quote(
            input_mint=input_mint,
            output_mint=output_mint,
            amount_atomic=amount_atomic,
            slippage_bps=slippage,
            fee_bps=fee_bps,
        )

        out_amount = quote.get("outAmount")
        price_impact = quote.get("priceImpactPct")
        route_plan = quote.get("routePlan", [])
        summary = (
            f"Quote ready.\\n"
            f"inAmount={quote.get('inAmount')}\\n"
            f"outAmount={out_amount}\\n"
            f"priceImpactPct={price_impact}\\n"
            f"routeHops={len(route_plan)}\\n"
            f"fee={fee_bps}bps"
        )

        if not execute:
            await message.answer(summary)
            return

        tx_sig = await dex.swap(quote_response=quote, output_mint=output_mint)
        await message.answer(f"{summary}\\nSwap submitted. tx: https://solscan.io/tx/{tx_sig}")

    except Exception as exc:
        await message.answer(f"Error: {exc}")


@dp.message(Command("quote"))
async def quote_cmd(message: Message) -> None:
    await _quote_or_swap(message, execute=False)


@dp.message(Command("swap"))
async def swap_cmd(message: Message) -> None:
    await _quote_or_swap(message, execute=True)


@dp.message(F.text)
async def fallback(message: Message) -> None:
    await message.answer(HELP)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
