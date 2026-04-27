# EACO 海外 WEB3 / WEB4 支付基础货币发展方案（2026）

> 面向目标：让 EACO 成为海外 Web3/Web4 支付的“可用、可结算、可增长”基础数字货币之一。

## 1. 三层目标模型

1) **交易层（Can Trade）**：
- 深化 E/SOL、E/USDT 流动性，维持低滑点、低冲击交易。
- 统一做市与风控参数（最大单笔、单地址频率、异常价格偏离告警）。

2) **支付层（Can Pay）**：
- 用 `web4sdk` 落地标准支付接口：`createQuote`, `createPayment`, `confirmPayment`, `refund`, `webhook`。
- 支持 B2C/B2B 场景：电商、SaaS订阅、TG MiniApp、跨境服务结算。

3) **资产层（Can Hold）**：
- 公开资金池和储备看板（PoR）。
- 明确手续费分配：LP 激励 / 回购销毁 / 生态基金。

## 2. 闭环产品架构（EACO Payment Loop）

- 用户入口：Telegram Bot / Web 小程序 / 商户插件
- 路由层：Jupiter 报价与路由执行
- 记账层：订单、交易、退款、佣金、推荐关系
- 风控层：钱包确权、KYC/AML 分级、黑名单/制裁名单筛查
- 结算层：商户自动结算（EACO 或 USDT）
- 增长层：多语言邀请裂变 + 大使 KPI

## 3. 关键执行路线（12 周版本）

### Phase A（1-4 周）：支付 MVP
- 发布商户收款 API（测试网/小额主网）
- 支持“创建订单 → 支付 → 回调 → 对账”
- 完成退款接口与状态机

### Phase B（5-8 周）：全球化运营
- 多语言模板：EN/ES/AR/FR/RU/JA/ZH
- TG 群组增长面板（拉新、留存、成交）
- 志愿者 1-6 月考核体系产品化

### Phase C（9-12 周）：资产与信用
- 链上 PoR 看板
- 做市/库存管理策略上线
- 商户等级费率 + 结算 SLA

## 4. 经济模型建议

- 手续费总区间：0.15% - 0.75%
- 推荐分配（可治理调整）：
  - 40% LP 激励
  - 30% 回购/销毁
  - 20% 生态基金
  - 10% 运营与安全预算

## 5. 成功指标（North Star）

- 月活支付钱包数（MPW）
- 商户数与复购率
- 平均支付成功率与结算时延
- 30 天留存与邀请转化率
- 链上流动性深度与滑点稳定性

## 6. 与 web4sdk 的直接结合建议

参考仓库：`https://github.com/eaco-group/web4sdk`

优先补齐以下 SDK 模块：
- `payments/quote.ts`
- `payments/checkout.ts`
- `payments/refund.ts`
- `payments/webhook-verify.ts`
- `risk/wallet-ownership.ts`
- `growth/referral.ts`

并提供：
- TypeScript SDK
- REST API OpenAPI 文档
- Postman Collection
- 商户接入样例（Node/Python）
