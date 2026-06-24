# -*- coding: utf-8 -*-
"""Lexicon-based explicit/NSFW detector for Vietnamese text.

Two matching layers (because de-accenting Vietnamese collides with normal words):

1. SAFE_DEACCENT — Sino-Vietnamese clinical terms whose de-accented form does NOT
   collide with common words (e.g. "duong vat", "xuat tinh"). Matched on de-accented
   text -> tolerant to FONT-CORRUPTED text (missing diacritics), common in scraped data.

2. ACCENT — terms whose de-accented form WOULD collide with normal words
   ("dâm đãng" vs "đảm đang", "bắn tinh" vs "bản tính", "nứng" vs "nung nấu") plus
   native Vietnamese slang. Matched WITH diacritics on NFC text -> high precision.

Counting word density (not a single hit) keeps precision high: erotica repeats these
terms heavily, while clean romance barely uses them.
"""
from __future__ import annotations

import re
import unicodedata

DEFAULT_HIT_THRESHOLD = 3  # a chunk is "explicit" if it matches >= this many keywords

# --- Layer 1: de-accented (font-tolerant). Audited: de-accented form has no common collision. ---
SAFE_DEACCENT = [
    # genitalia (clinical Sino-Vietnamese)
    "duong vat", "am dao", "am ho", "am vat", "am he", "duong can", "duong cu",
    "ngoc hanh", "quy dau", "cu vat", "nhuc bong", "num vu",
    "hoa huyet", "mat huyet", "hau huyet", "huyet khau", "hau dinh",
    # fluids
    "tinh dich", "xuat tinh", "phun tinh", "phong tinh", "dam thuy", "dam dich", "bach dich",
    # acts
    "lam tinh", "giao hop", "giao cau", "giao hoan", "an ai", "khau giao",
    "tham nhap", "dam vao", "dut vao", "cam vao", "thoc vao", "dam thuc", "tien nhap",
    "dau luoi", "dao luoi", "liem", "bu mut", "co xat", "cuong cung",
    # states / arousal
    "dam duc", "dam tien", "phat tinh", "sac tinh", "cuc khoai", "khoai cam", "khoai lac",
    # undressing / nudity
    "khoa than", "tran truong", "tran trui", "coi quan", "quan lot", "tuot quan", "lo than",
    # sexual crimes
    "hiep dam", "cuong gian", "cuong hiep", "thu dam", "loan luan", "thong dam",
]

# --- Layer 2: matched WITH diacritics (high precision). Homograph-prone + native slang. ---
ACCENT = [
    # Sino-Vietnamese that collide when de-accented -> must keep diacritics
    "dâm đãng", "dâm loạn", "bắn tinh", "đăng đỉnh", "lên đỉnh", "động dục",
    "nhũ hoa", "đầu ngực", "trương to", "phòng the", "truy hoan", "hoan ái", "lẳng lơ",
    "dâm phụ", "dâm dật", "bạo dâm", "cuồng dâm", "cuồng dục", "dục tình",
    "kích dục", "kích dâm", "hãm hiếp", "gạ tình",
    # native Vietnamese vulgar (diacritics distinguish: buồi!=buổi, địt!=đít, lồn!=lớn, nứng!=nung)
    "lồn", "cặc", "buồi", "địt", "đụ", "nứng", "chịch", "lìn",
    "bú cặc", "địt nhau", "đụ nhau", "phá trinh",
]

_NON_AZ = re.compile(r"[^a-z\s]+")
_WS = re.compile(r"\s+")
_PUNCT_U = re.compile(r"[^\w]+", re.UNICODE)
_SAFE_PATTERN = re.compile(r"\b(?:" + "|".join(re.escape(t) for t in SAFE_DEACCENT) + r")\b")
_ACCENT_PATTERN = re.compile(r"\b(?:" + "|".join(re.escape(t) for t in ACCENT) + r")\b", re.UNICODE)


def deaccent(s: str) -> str:
    """Lowercase + strip Vietnamese diacritics + đ->d. Merges proper diacritics AND
    font-corrupted (missing-mark) variants into one accent-free form."""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d")
    s = _NON_AZ.sub(" ", s)
    return _WS.sub(" ", s).strip()


def _norm_keep(s: str) -> str:
    """NFC + lowercase, KEEP diacritics (to match native vulgar terms)."""
    s = unicodedata.normalize("NFC", s.lower())
    s = _PUNCT_U.sub(" ", s)
    return _WS.sub(" ", s).strip()


def count_hits(text: str) -> int:
    """Total explicit-keyword matches: de-accent layer (font-tolerant) + accent layer (precise)."""
    return len(_SAFE_PATTERN.findall(deaccent(text))) + len(_ACCENT_PATTERN.findall(_norm_keep(text)))


def is_explicit(text: str, threshold: int = DEFAULT_HIT_THRESHOLD) -> bool:
    """True if the text matches >= `threshold` explicit keywords."""
    return count_hits(text) >= threshold
