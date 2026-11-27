"""本月该买清单：规格、价格带、渠道、可直接复制的采购文本。"""

from __future__ import annotations

from datetime import date

from ..domain.engine import DueItem
from ..ports import LLMPort, StorePort
from .run import scan


def _window(items: list[DueItem], today: date) -> list[DueItem]:
    return [i for i in items if i.days_left <= 30]


def build_report(
    store: StorePort, today: date, llm: LLMPort | None = None
) -> tuple[str, list[DueItem], list]:
    items, findings = scan(store, today, llm)
    due = _window(items, today)
    lines = [
        f"# 本月该买清单 · {today.year} 年 {today.month} 月",
        "",
        f"> 按使用强度折算后的到期日；共 {len(due)} 项在 30 天内到期。"
        f"{' 规格与价格带由 30 型号目录 + 模型补全，数字以本地目录为准。' if llm is not None else ' 本次未调用模型，规格/价格/渠道全部来自本地目录。'}",
        "",
        "## 一、采购清单",
        "",
        "| 家电 / 型号 | 耗材 | 规格 | 参考价 | 渠道 | 到期 | 动作 |",
        "| --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for item in due:
        lines.append(
            f"| {item.appliance} {item.model} | {item.consumable} | {item.spec or '待确认'} | "
            f"{item.price_low:g}-{item.price_high:g} 元 | {item.channel or '待确认'} | "
            f"{item.due_on.isoformat()}（{item.days_left} 天） | {item.action} |"
        )
    if not due:
        lines.append("| - | 本月没有 30 天内到期的耗材 | - | - | - | - | - |")
    lines += ["", "## 二、一键复制到微信", "", "```text", f"{today.month} 月要买的耗材："]
    for item in due:
        lines.append(
            f"{item.appliance}{item.model}·{item.consumable}｜{item.spec or '规格待确认'}｜"
            f"{item.price_low:g}-{item.price_high:g} 元｜{item.channel or '渠道待确认'}"
        )
    if not due:
        lines.append("本月无到期耗材，不用买。")
    lines += [
        "```",
        "",
        "## 三、为什么是这些日期",
        "",
        "- 到期日 = 上次更换日 + 周期 ÷ 使用强度；不是固定月数。",
        "- 库存为 0 的标“购买”，有库存的标“更换”；换下来的旧件先别扔，拍照对照规格。",
        "- 价格带越出本地目录的模型报价会被丢弃，清单仍保留目录价格，不会整条消失。",
        "",
    ]
    if findings:
        lines += ["## 四、需要人工确认", ""]
        for f in findings[:8]:
            lines.append(f"- {f.message}")
        lines.append("")
    lines += [
        "---",
        "",
        "数据口径：30 个常见型号的耗材周期、价格带、渠道为本地目录；模型只能补规格与更窄的价格，不能改数字。",
        "",
    ]
    return "\n".join(lines), due, findings
