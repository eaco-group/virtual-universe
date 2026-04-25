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

---

## 原始 README 内容保留（方便全球网友查看）

# virtual-universe
virtual universe，How can eaco integrate with the virtual universe and facilitate the circulation and use of eaco within it?


## about eaco

The only $eaco in the universe and the earth,

EACO ($eaco) is an innovative small currency, the only $eaco in the universe and the earth,

CA:

DqfoyZH96RnvZusSp3Cdncjpyp3C74ZmJzGhjmHnDHRH

As the MEME coin of villagers around the Earth, EACO aims to promote environmental protection and sustainable development, integrate decentralized finance and digital assets, and become the representative of future personal core assets.

EACO(Earth's Best Coin)

CA:

DqfoyZH96RnvZusSp3Cdncjpyp3C74ZmJzGhjmHnDHRH

https://orbmarkets.io/token/DqfoyZH96RnvZusSp3Cdncjpyp3C74ZmJzGhjmHnDHRH

https://www.orca.so/pools?tokens=DqfoyZH96RnvZusSp3Cdncjpyp3C74ZmJzGhjmHnDHRH

https://raydium.io/swap/?inputMint=sol&outputMint=DqfoyZH96RnvZusSp3Cdncjpyp3C74ZmJzGhjmHnDHRH

https://discord.gg/HWsweV6fFy




## 加入Coze Agent World：https://world.coze.site/skill.md

 EACO 成功入驻coze Agent World！2026

🌍 EACO × Agent World 集成 — 完成报告

🎯 已完成

1. Agent World 注册 ✅

Agent Name: eaco-global

Agent ID: f649c870-99cd-4e9a-8223-8a8a06520094

Agent URL: https://world.coze.site/agent/f649c870-99cd-4e9a-8223-8a8a06520094


2. Synthetic Exchange 参赛 ✅

比赛 ID: match_1777000323458

席位: 1/8（已锁定）

状态: waiting（等待8位Agent参赛后启动）

观战: https://synthetic.coze.site/match/match_1777000323458

3. 跨平台曝光 ✅

135,248+ 个 AI Agent 已覆盖

全球开发者/用户可通过 Agent World 发现 EACO

📊 EACO 全球 Agent 网络

渠道    状态    覆盖

Agent World    ✅ 已入驻    135,248+ Agent

Telegram 7群    ✅ 运行中    6亿+用户

Twitter    ⚠️ 受限    海外主战场

Discord    ⚠️ 受限    社区频道

📁 已创建文件

openclaw/config/skills/eaco-agent-world/SKILL.md — Agent World 技能

memory/2026-04-24.md — 记忆已更新

⚠️ 注意事项

合成交易所需要 8 位 Agent 参赛才启动交易

可邀请其他 EACO 社区成员也入驻 Agent World，共同推动开赛


## How can EACO evolve into “EACO — Earth’s Best WEB3 + AI + RWA Coin”? 

What approaches and methods can make this possible?
