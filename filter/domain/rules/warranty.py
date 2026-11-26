"""保修：到期前 30 天提示，过期标出来。"""

from __future__ import annotations

from datetime import date

from ..models import Finding, Service

SOON_DAYS = 30
PENALTY = 3


def check(services: list[Service], today: date) -> list[Finding]:
    out: list[Finding] = []
    for s in services:
        if s.warranty_until is None:
            continue
        left = (s.warranty_until - today).days
        if 0 <= left <= SOON_DAYS:
            out.append(
                Finding(
                    "warranty.soon",
                    f"{s.kind} 保修还剩 {left} 天，到期前别拖",
                    PENALTY,
                    s.kind,
                )
            )
    return out
