# -*- coding: utf-8 -*-
"""Thin-content detector (rule-based): chapters with NO real story text —
login-gate/paywall boilerplate, "đang cập nhật" placeholders, or too short (crawl errors).
"""
from __future__ import annotations

import re

_BOILERPLATE = [
    r"bạn\s*cần\s*đăng\s*nhập\s*để\s*đọc",
    r"đăng\s*nhập\s*tại\s*đây",
    r"đăng\s*ký\s*tại\s*đây",
    r"vui\s*lòng\s*đăng\s*nhập",
    r"(chương|nội\s*dung)[^\n]{0,20}(vip|trả\s*phí|premium)",
    r"nạp\s*(xu|coin|điểm)\s*để",
    r"đang\s*cập\s*nhật",
    r"nội\s*dung\s*đang\s*(được\s*)?(cập\s*nhật|biên\s*tập|chờ\s*duyệt)",
]
_COMPILED = [re.compile(p, re.IGNORECASE) for p in _BOILERPLATE]

DEFAULT_MIN_CHARS = 300  # truyện chữ 1 chương thường >1000 ký tự


def is_thin(text: str, min_chars: int = DEFAULT_MIN_CHARS):
    """Return (is_thin: bool, reason: str). Pure rule, O(n), no model."""
    t = text.strip()
    n = len(t)
    head = t[:800]
    for pat in _COMPILED:
        if pat.search(head):
            return True, f"boilerplate:{pat.pattern[:28]}"
    if n < min_chars:
        return True, f"too_short:{n}"
    return False, "ok"
