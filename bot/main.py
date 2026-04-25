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

SUPPORTED_LANGS = {"en", "zh", "es", "ar", "fr", "ru", "ja"}

HELP = {
    "en": (
        "EACO DEX Bot commands:\n"
        "/start [ref_code] - register user\n"
        "/help - show help\n"
        "/wallet - show bot wallet pubkey\n"
        "/fee - show your fee bps\n"
        "/setfee <15-75> - set your fee bps\n"
        "/setlang <en|zh|es|ar|fr|ru|ja> - switch language\n"
        "/invite - get global invite link\n"
        "/myref - show referral count\n"
        "/quote <inputMint:decimals> <outputMint:decimals> <amount> [slippageBps]\n"
        "/swap <inputMint:decimals> <outputMint:decimals> <amount> [slippageBps]\n"
        "/verifywallet <wallet> - start wallet ownership challenge\n"
        "/verifytx <verify_id> <tx_hash> - submit proof tx\n"
        "/volunteer_apply - apply for 1-6 month volunteer cycle\n"
        "/refund_policy - show refund clause"
    ),
    "zh": (
        "EACO DEX 机器人命令：\n"
        "/start [ref_code] - 注册用户\n"
        "/help - 帮助\n"
        "/wallet - 查看机器人钱包\n"
        "/fee - 查看费率\n"
        "/setfee <15-75> - 设置费率(bps)\n"
        "/setlang <en|zh|es|ar|fr|ru|ja> - 切换语言\n"
        "/invite - 获取全球邀请链接\n"
        "/myref - 查看邀请人数\n"
        "/quote <输入mint:精度> <输出mint:精度> <数量> [滑点bps]\n"
        "/swap <输入mint:精度> <输出mint:精度> <数量> [滑点bps]\n"
        "/verifywallet <钱包> - 发起钱包确权挑战\n"
        "/verifytx <验证ID> <tx_hash> - 提交链上证明\n"
        "/volunteer_apply - 申请1-6个月志愿者考核\n"
        "/refund_policy - 查看退款条款"
    ),
}

REFUND_POLICY = (
    "Refund & Performance Clause:\n"
    "1) If paid promotion/liquidity tasks are not executed as agreed, partner should refund fully/partially.\n"
    "2) Evidence must be on-chain or with auditable logs.\n"
    "3) Volunteer cycle is 1-6 months with measurable KPIs.\n"
)

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


def text_for(user_id: int, key: str) -> str:
    user = storage.get_user(user_id)
    lang = str(user["language"])
    if key == "help":
        if lang == "zh":
            return HELP["zh"]
        return HELP["en"]
    return HELP["en"]


def parse_start_ref(message: Message) -> str | None:
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        return None
    return parts[1].strip()


@dp.message(Command("start"))
async def start(message: Message) -> None:
    user_id = int(message.from_user.id)
    username = message.from_user.username
    storage.ensure_user(user_id, username=username)

    ref_code = parse_start_ref(message)
    ref_bind_ok = False
    if ref_code:
        ref_bind_ok = storage.bind_referral(user_id, ref_code)

    suffix = ""
    if ref_code:
        suffix = "\nReferral bind: success" if ref_bind_ok else "\nReferral bind: skipped/invalid"

    await message.answer(
        "Welcome to EACO DEX Bot.\n"
        "Supports Solana token swaps via Jupiter aggregator.\n"
        f"Fee range: {settings.fee_min_bps/100:.2f}% - {settings.fee_max_bps/100:.2f}%"
        f"{suffix}"
    )


@dp.message(Command("help"))
async def help_cmd(message: Message) -> None:
    user_id = int(message.from_user.id)
    storage.ensure_user(user_id, username=message.from_user.username)
    await message.answer(text_for(user_id, "help"))


@dp.message(Command("setlang"))
async def set_lang_cmd(message: Message) -> None:
    user_id = int(message.from_user.id)
    parts = (message.text or "").split()
    if len(parts) != 2:
        await message.answer("Usage: /setlang <en|zh|es|ar|fr|ru|ja>")
        return
    lang = parts[1].lower()
    if lang not in SUPPORTED_LANGS:
        await message.answer("Unsupported language")
        return
    storage.set_language(user_id, lang)
    await message.answer(f"Language updated: {lang}")


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
    parts = (message.text or "").split()
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


@dp.message(Command("invite"))
async def invite_cmd(message: Message) -> None:
    user_id = int(message.from_user.id)
    code, count = storage.referral_stats(user_id)
    if settings.bot_username:
        link = f"https://t.me/{settings.bot_username}?start={code}"
    else:
        link = f"<set BOT_USERNAME in .env>?start={code}"
    await message.answer(f"Your referral code: {code}\nInvites: {count}\nInvite link: {link}")


@dp.message(Command("myref"))
async def myref_cmd(message: Message) -> None:
    user_id = int(message.from_user.id)
    code, count = storage.referral_stats(user_id)
    await message.answer(f"Referral code: {code}\nTotal invited users: {count}")


@dp.message(Command("verifywallet"))
async def verifywallet_cmd(message: Message) -> None:
    user_id = int(message.from_user.id)
    parts = (message.text or "").split()
    if len(parts) != 2:
        await message.answer("Usage: /verifywallet <sol_wallet_address>")
        return
    wallet = parts[1].strip()
    record = storage.create_wallet_verification(user_id, wallet)
    await message.answer(
        "Wallet verification challenge created:\n"
        f"verify_id={record['id']}\n"
        f"Step1: Bot sends {record['send_amount']} EACO test units (off-chain arrangement).\n"
        f"Step2: Return {record['return_amount']} EACO to official wallet.\n"
        "Step3: Submit tx hash with /verifytx <verify_id> <tx_hash>."
    )


@dp.message(Command("verifytx"))
async def verifytx_cmd(message: Message) -> None:
    user_id = int(message.from_user.id)
    parts = (message.text or "").split()
    if len(parts) != 3:
        await message.answer("Usage: /verifytx <verify_id> <tx_hash>")
        return

    verify_id = int(parts[1])
    tx_hash = parts[2]
    exists = False
    try:
        exists = dex.tx_exists(tx_hash)
    except Exception:
        exists = False

    if not exists:
        await message.answer("tx hash not found on chain yet, please retry after confirmation.")
        return

    ok = storage.submit_wallet_verification(user_id, verify_id, tx_hash)
    if not ok:
        await message.answer("verification record not found or not pending")
        return
    await message.answer("Verification proof submitted. Admin will review and approve.")


@dp.message(Command("approve_verify"))
async def approve_verify_cmd(message: Message) -> None:
    user_id = int(message.from_user.id)
    if user_id not in settings.admin_ids:
        await message.answer("admin only")
        return

    parts = (message.text or "").split()
    if len(parts) != 2:
        await message.answer("Usage: /approve_verify <verify_id>")
        return
    verify_id = int(parts[1])
    ok = storage.approve_wallet_verification(verify_id)
    await message.answer("approved" if ok else "not found or not submitted")


@dp.message(Command("volunteer_apply"))
async def volunteer_apply_cmd(message: Message) -> None:
    user_id = int(message.from_user.id)
    storage.set_volunteer_status(user_id, "applied")
    await message.answer(
        "Volunteer application submitted.\n"
        "Assessment cycle: 1-6 months with KPI review (traffic, holders, liquidity contribution)."
    )


@dp.message(Command("refund_policy"))
async def refund_policy_cmd(message: Message) -> None:
    await message.answer(REFUND_POLICY)


@dp.message(Command("stats"))
async def stats_cmd(message: Message) -> None:
    user_id = int(message.from_user.id)
    if user_id not in settings.admin_ids:
        await message.answer("admin only")
        return
    s = storage.global_stats()
    await message.answer(
        "Global stats:\n"
        f"users={s['users']}\n"
        f"referrals={s['referrals']}\n"
        f"verified_wallets={s['verified_wallets']}\n"
        f"successful_swaps={s['successful_swaps']}"
    )


async def _quote_or_swap(message: Message, execute: bool) -> None:
    user_id = int(message.from_user.id)
    storage.ensure_user(user_id, username=message.from_user.username)

    parts = (message.text or "").split()
    if len(parts) < 4:
        await message.answer("Usage: /quote|/swap <inputMint:decimals> <outputMint:decimals> <amount> [slippageBps]")
        return

    try:
        input_mint, input_decimals = parse_mint_and_decimals(parts[1])
        output_mint, _output_decimals = parse_mint_and_decimals(parts[2])
        amount = float(parts[3])
        slippage = int(parts[4]) if len(parts) > 4 else 100
        if slippage < 10 or slippage > 500:
            raise ValueError("slippage bps must be between 10 and 500")

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
        storage.log_trade(
            telegram_id=user_id,
            input_mint=input_mint,
            output_mint=output_mint,
            amount_atomic=amount_atomic,
            fee_bps=fee_bps,
            slippage_bps=slippage,
            status="success",
            tx_hash=tx_sig,
        )
        await message.answer(f"{summary}\\nSwap submitted. tx: https://solscan.io/tx/{tx_sig}")

    except Exception as exc:
        storage.log_trade(
            telegram_id=user_id,
            input_mint=parts[1] if len(parts) > 1 else "",
            output_mint=parts[2] if len(parts) > 2 else "",
            amount_atomic=0,
            fee_bps=storage.get_fee_bps(user_id),
            slippage_bps=0,
            status="failed",
            error=str(exc),
        )
        await message.answer(f"Error: {exc}")


@dp.message(Command("quote"))
async def quote_cmd(message: Message) -> None:
    await _quote_or_swap(message, execute=False)


@dp.message(Command("swap"))
async def swap_cmd(message: Message) -> None:
    await _quote_or_swap(message, execute=True)


@dp.message(F.text)
async def fallback(message: Message) -> None:
    user_id = int(message.from_user.id)
    storage.ensure_user(user_id, username=message.from_user.username)
    await message.answer(text_for(user_id, "help"))


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
