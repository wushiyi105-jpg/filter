# 更新记录

## Unreleased

- 新增 `report`：本月采购清单、规格、价格带、渠道与可复制微信文本
- 30 个常见型号目录，含耗材周期、参考价与购买渠道
- 模型越界只丢价格，清单与规格/渠道保留
- `0001_init` 改为显式 `op.create_table` / `op.create_index`，运行期走 `alembic upgrade`
- `app/` 只依赖 `ports`，新增内存假实现用例
- 开 ruff `E2`/`E3`；CI 增加 `docker build` 与 `/health` 探活

## 1.0.0

- 周期推算（含使用强度、跨月、闰年）
- 耗材余量与待购
- 保修 30 天窗口
- 价格守卫
- 每日到期推送（幂等键含日期与耗材）
- CLI 与 Web 双入口
