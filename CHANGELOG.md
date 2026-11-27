# 更新记录

## Unreleased

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
