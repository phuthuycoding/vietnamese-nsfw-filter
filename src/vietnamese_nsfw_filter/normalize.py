# -*- coding: utf-8 -*-
"""Mechanical text normalization for scraped Vietnamese text (rule-based, no model).

Chỉ chuẩn hoá cơ học — KHÔNG sửa chính tả, KHÔNG đổi từ ngữ:
  - Unicode -> NFC (gộp dấu tổ hợp tiếng Việt)
  - nbsp / khoảng trắng unicode lạ -> space; bỏ zero-width/BOM
  - CRLF -> LF, tab -> space
  - gộp khoảng trắng thừa, bỏ space trước dấu câu
  - gộp nhiều dòng trống thành tối đa 1
"""
from __future__ import annotations

import re
import unicodedata

_UNICODE_SPACE = re.compile(r"[   -   　]")
_ZERO_WIDTH = re.compile(r"[﻿​‌‍⁠]")
_SPACE_BEFORE_PUNCT = re.compile(r"[ ]+([,.;:!?…)\]}»])")
_MULTISPACE = re.compile(r"[ ]{2,}")
_MULTIBLANK = re.compile(r"\n{3,}")


def normalize(text: str) -> str:
    """Normalize one text block. Idempotent (running again changes nothing)."""
    t = unicodedata.normalize("NFC", text)
    t = _ZERO_WIDTH.sub("", t)
    t = _UNICODE_SPACE.sub(" ", t)
    t = t.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    lines = []
    for line in t.split("\n"):
        line = _MULTISPACE.sub(" ", line)
        line = _SPACE_BEFORE_PUNCT.sub(r"\1", line)
        lines.append(line.strip())
    t = "\n".join(lines)
    t = _MULTIBLANK.sub("\n\n", t).strip()
    return t + "\n" if t else ""
