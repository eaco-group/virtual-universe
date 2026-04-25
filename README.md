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
- `BOT_USERNAME`
- `ADMIN_IDS`

## 闭环能力升级（本次新增）

围绕你提出的“EACO 在虚拟宇宙流通 + 全球社区运营闭环”，本次代码把机器人升级为以下能力：

1. **链上交易闭环**
   - `/quote` + `/swap` 继续走 Jupiter 聚合路由，支持 Solana 代币对换。
   - 增加滑点边界检查（10~500 bps）和交易日志记录（成功/失败）。
2. **多用户运营闭环**
   - 多用户资料扩展：`username / language / referral_code / invited_by / wallet_verified / volunteer_status`。
   - 支持邀请裂变：`/invite`、`/myref`，自动统计拉新人数。
3. **钱包确权闭环**
   - `/verifywallet <wallet>` 发起确权挑战，生成 `verify_id` 与挑战数量。
   - `/verifytx <verify_id> <tx_hash>` 提交链上证明，管理员 `/approve_verify` 审核通过。
4. **多语言入口**
   - `/setlang <en|zh|es|ar|fr|ru|ja>`，中英文帮助文案已落地，其他语种可继续扩充。
5. **志愿者 + 退款条款闭环**
   - `/volunteer_apply` 申请 1~6 个月考核周期。
   - `/refund_policy` 输出履约退款条款说明。
6. **管理后台最小闭环**
   - `/stats`（admin only）查看用户、邀请、确权、交易成功数。

> 说明：你给的 ChatGPT share 链接是登录墙页面，自动化环境无法直接读取正文；`whitepaper` 页面可访问标题但正文为前端动态渲染。当前改造依据你在仓库和对话中给出的 EACO 规则落地。

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

## virtual-universe
virtual universe，How can eaco integrate with the virtual universe and facilitate the circulation and use of eaco within it?

## about eaco

The only $eaco in the universe and the earth,
EACO ($eaco) is an innovative small currency, the only $eaco in the universe and the earth,
CA:
DqfoyZH96RnvZusSp3Cdncjpyp3C74ZmJzGhjmHnDHRH
As the MEME coin of villagers around the Earth, EACO aims to promote environmental protection and sustainable development, integrate decentralized finance and digital assets, and become the representative of future personal core assets.

EACO(Earth's Best Coin)


https://orbmarkets.io/token/DqfoyZH96RnvZusSp3Cdncjpyp3C74ZmJzGhjmHnDHRH

https://www.orca.so/pools?tokens=DqfoyZH96RnvZusSp3Cdncjpyp3C74ZmJzGhjmHnDHRH

https://raydium.io/swap/?inputMint=sol&outputMint=DqfoyZH96RnvZusSp3Cdncjpyp3C74ZmJzGhjmHnDHRH

https://discord.gg/HWsweV6fFy

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
