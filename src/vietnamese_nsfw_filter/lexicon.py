# -*- coding: utf-8 -*-
"""Lexicon-based explicit/NSFW detector for Vietnamese text.

Matching layers (de-accenting Vietnamese collides with normal words, so we split):

1. SAFE_DEACCENT — Sino-Vietnamese / compound terms whose de-accented form does NOT
   collide with common words ("duong vat", "xuat tinh"). Matched on DE-ACCENTED text
   -> tolerant to FONT-CORRUPTED text (missing diacritics), common in scraped data.
2. ENGLISH — borrowed/loan explicit words (ascii), matched on de-accented text.
3. ACCENT — native vulgar + Sino-Vietnamese whose de-accented form WOULD collide
   ("dâm đãng" vs "đảm đang", "bắn tinh" vs "bản tính", "nứng" vs "nung nấu").
   Matched WITH diacritics on NFC text -> high precision.
4. WEAK (opt-in) — high-recall but FP-prone terms ("vú", "mông", "bú", "lên giường"...)
   counted only when `include_weak=True`.

Counting keyword DENSITY (not a single hit) keeps precision high: erotica repeats these
terms heavily, clean text barely uses them.
"""
from __future__ import annotations

import re
import unicodedata

DEFAULT_HIT_THRESHOLD = 3  # a chunk is "explicit" if it matches >= this many keywords

# --- Layer 1: de-accented, font-tolerant. Audited: de-accented form has no common collision. ---
SAFE_DEACCENT = [
    # genitalia (clinical Sino-Vietnamese / anatomical)
    "duong vat", "duong can", "duong cu", "duong khoi", "cuong vat",
    "am dao", "am ho", "am vat", "am he", "am mao",
    "ngoc hanh", "quy dau", "bao quy dau", "cu vat", "nhuc bong", "num vu",
    "hoa huyet", "mat huyet", "hau huyet", "huyet khau", "hau dinh", "hau mon",
    "hoa kinh", "noi am", "tinh hoan", "long mu", "tu cung", "ham huyet",
    # fluids
    "tinh dich", "tinh trung", "xuat tinh", "phun tinh", "phong tinh",
    "dam thuy", "dam dich", "ai dich", "hoa dich", "bach dich", "dam thui",
    # acts
    "lam tinh", "giao hop", "giao cau", "giao hoan", "giao phoi", "an ai", "hoan ai",
    "khau giao", "tham nhap", "dam vao", "dut vao", "cam vao", "thoc vao", "dam thuc",
    "tien nhap", "dao luoi", "dau luoi", "co xat", "cuong cung", "thu dam", "tu suong",
    "quan he tinh duc", "lam chuyen ay",
    # states / arousal / lust
    "dam duc", "dam loan", "dam tien", "dam dat", "dam o", "gian dam", "ta dam",
    "au dam", "phat tinh", "sac tinh", "sac duc", "cuc khoai", "khoai cam", "khoai lac",
    "xuan tinh", "cuong dam", "cuong duc", "duc vong", "duc tinh", "hieu dam", "hao sac",
    "dam buc", "thong dam", "loan luan", "nhuc duc", "tham duc",
    # crimes / prostitution
    "hiep dam", "cuong gian", "cuong hiep", "kich duc", "kich dam", "ham hiep", "ga tinh",
    "mai dam", "ban dam", "gai goi", "gai diem", "diem dang", "lau xanh", "nha tho",
]

# --- Layer 2: borrowed English explicit words (ascii, matched on de-accented text). ---
ENGLISH = [
    "sex", "sexy", "sextoy", "porn", "porno", "pornhub", "xnxx", "xvideos",
    "jav", "hentai", "nsfw", "xxx", "fuck", "fucking", "dick", "cock", "pussy",
    "blowjob", "handjob", "footjob", "deepthroat", "orgasm", "masturbate", "masturbation",
    "nude", "naked", "horny", "boobs", "boob", "tits", "nipple", "penis", "vagina",
    "anal", "milf", "gangbang", "threesome", "bdsm", "dildo", "vibrator", "erotic",
    "slut", "whore", "cunt", "clit", "bisexual", "camgirl", "onlyfans", "creampie",
]

# --- Layer 3: matched WITH diacritics (precise). Native vulgar + homograph-prone Sino-Viet. ---
ACCENT = [
    # teencode chửi tục viết tắt (rõ nghĩa NSFW)
    "vcl", "vkl", "vlz", "clmm", "đcm", "đkm", "đmm", "đệt", "đậu má", "đậu xanh rau má",
    "đĩ", "đĩ chó", "máu dâm", "dê xồm", "dê già", "biến thái", "dâm tặc",
    # vulgar / profanity compounds
    "địt mẹ", "địt mẹ mày", "đụ má", "đụ mẹ", "đéo mẹ", "vãi lồn", "vãi cặc",
    "bú lồn", "ăn cặc", "bú cặc", "bú buồi", "liếm lồn", "mút cặc",
    "địt nhau", "đụ nhau", "chịch nhau", "phang nhau", "xoạc nhau", "vét máng",
    "chịch choạc", "gạ chịch", "gạ địt", "đút buồi", "nhét cặc",
    "nứng lồn", "nứng cặc", "nứng tình", "đầu buồi", "hòn dái", "bóp dái",
    "gái điếm", "đĩ điếm", "con điếm", "phá trinh",
    # Sino-Vietnamese that collide when de-accented -> keep diacritics
    "dâm đãng", "dâm phụ", "dâm dật", "dâm tà", "bạo dâm", "cuồng dâm", "hiếu dâm",
    "bắn tinh", "phóng tinh", "đăng đỉnh", "lên đỉnh", "động dục", "trương to",
    "nhũ hoa", "đầu ngực", "phòng the", "truy hoan", "lẳng lơ", "cưỡng bức",
    "mây mưa", "vân vũ", "ái ân", "ân ái", "động phòng",
]

# --- Layer 4 (OPT-IN): high-recall, FP-prone. Only counted when include_weak=True. ---
# Gồm tiếng lóng / vùng miền / ẩn dụ — đa nghĩa nên FP cao (chim/bướm/cu = con vật, cô bé = bé gái...).
WEAK = [
    # bộ phận (đời thường, dễ FP)
    "vú", "mông", "ngực", "dái", "đùi non", "eo thon", "ngực trần", "khe ngực",
    # hành vi (đời thường)
    "bú", "mút", "liếm", "đút", "nhét", "thọc", "vê", "bóp", "sờ", "sờ soạng",
    "lên giường", "ngủ với", "quan hệ", "động phòng", "ham muốn", "thèm khát",
    "khỏa thân", "trần truồng", "trần như nhộng", "lõa thể",
    "rên rỉ", "rên la", "thở dốc", "hổn hển", "ướt đẫm", "khêu gợi", "gợi cảm", "phê",
    # lóng / vùng miền / ẩn dụ bộ phận (đa nghĩa -> FP)
    "chim", "bướm", "cu", "cò", "cậu nhỏ", "thằng nhỏ", "cô bé", "của quý",
    "chỗ ấy", "chỗ kín", "vùng kín", "tam giác mật", "núi đôi", "gò bồng đảo",
    "đào tiên", "bưởi", "quả đào", "làm nháy", "quất", "chén", "xơi",
    # teencode chửi mơ hồ (ngắn, dễ FP)
    "vl", "đm", "dm", "cc", "vãi",
]

_NON_AZ = re.compile(r"[^a-z\s]+")
_WS = re.compile(r"\s+")
_PUNCT_U = re.compile(r"[^\w]+", re.UNICODE)


def _build(terms):
    return re.compile(r"\b(?:" + "|".join(re.escape(t) for t in terms) + r")\b", re.UNICODE)


# Native vulgar stems matched REPEAT-TOLERANT to defeat character-stretching evasion
# ("địtttt", "lồnnn", "đụuu"). Diacritics keep them distinct from normal words.
NATIVE_VULGAR = ["lồn", "cặc", "buồi", "địt", "đụ", "nứng", "chịch", "lìn"]

_DEACCENT_PATTERN = _build(SAFE_DEACCENT + ENGLISH)
_ACCENT_PATTERN = _build(ACCENT)
_WEAK_PATTERN = _build(WEAK)
_NATIVE_PATTERN = re.compile(
    r"\b(?:" + "|".join(re.escape(t) + "+" for t in NATIVE_VULGAR) + r")\b", re.UNICODE
)


def deaccent(s: str) -> str:
    """Lowercase + strip Vietnamese diacritics + đ->d. Merges proper diacritics AND
    font-corrupted (missing-mark) variants into one accent-free form."""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.replace("đ", "d")
    s = _NON_AZ.sub(" ", s)
    return _WS.sub(" ", s).strip()


def _norm_keep(s: str) -> str:
    """NFC + lowercase, KEEP diacritics (to match native vulgar / homograph terms)."""
    s = unicodedata.normalize("NFC", s.lower())
    s = _PUNCT_U.sub(" ", s)
    return _WS.sub(" ", s).strip()


def count_hits(text: str, include_weak: bool = False) -> int:
    """Total explicit-keyword matches.

    Default = precision-tuned (de-accent clinical/English + accented native/homograph).
    `include_weak=True` adds the high-recall WEAK layer (more catches, more false positives).
    """
    deacc = deaccent(text)
    keep = _norm_keep(text)
    n = (len(_DEACCENT_PATTERN.findall(deacc))
         + len(_ACCENT_PATTERN.findall(keep))
         + len(_NATIVE_PATTERN.findall(keep)))
    if include_weak:
        n += len(_WEAK_PATTERN.findall(keep))
    return n


def is_explicit(text: str, threshold: int = DEFAULT_HIT_THRESHOLD, include_weak: bool = False) -> bool:
    """True if the text matches >= `threshold` explicit keywords."""
    return count_hits(text, include_weak=include_weak) >= threshold
