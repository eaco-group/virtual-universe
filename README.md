# virtual-universe

EACO DEX Bot（Telegram）参考实现：
- 支持 Solana 链代币交易（通过 Jupiter 聚合路由）。
- 支持多用户（SQLite 存储用户费率）。
- 手续费支持 0.15% - 0.75%（15-75 bps）可配置。
- 支持按用户设置费率：`/setfee 15..75`。

> ⚠️ 说明：代码为可运行基础版，生产环境请补充风控、限频、审计、HSM/托管签名、监控报警与法务合规。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

编辑 `.env`：
- `TELEGRAM_BOT_TOKEN`
- `SOLANA_PRIVATE_KEY_BASE58`（机器人钱包私钥）

可选：配置 `fee_accounts.json`（用于 Jupiter 平台费账户，键=输出 Mint，值=对应手续费 ATA 地址）。

## 运行

```bash
python bot/main.py
```

## 机器人命令

- `/start` 注册用户
- `/wallet` 查看机器人钱包地址
- `/fee` 查看当前费率
- `/setfee <15-75>` 设置手续费 bps
- `/quote <inputMint:decimals> <outputMint:decimals> <amount> [slippageBps]`
- `/swap <inputMint:decimals> <outputMint:decimals> <amount> [slippageBps]`

示例：

```text
/quote So11111111111111111111111111111111111111112:9 DqfoyZH96RnvZusSp3Cdncjpyp3C74ZmJzGhjmHnDHRH:6 0.5 100
```

## 目录

- `bot/main.py` Telegram 命令与业务入口
- `bot/dex_client.py` Jupiter quote/swap 与 Solana 交易签名广播
- `bot/storage.py` 多用户与费率持久化
- `bot/config.py` 环境变量配置加载
- `requirements.txt` 依赖

## 费用范围

- 最低：15 bps = 0.15%
- 最高：75 bps = 0.75%

可在 `.env` 中调整：
- `FEE_MIN_BPS`
- `FEE_MAX_BPS`
- `DEFAULT_FEE_BPS`
