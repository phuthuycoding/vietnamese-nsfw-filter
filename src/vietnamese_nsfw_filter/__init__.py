# -*- coding: utf-8 -*-
"""vietnamese-nsfw-filter — lexicon-based NSFW/explicit text detector for Vietnamese.

Quick start:
    from vietnamese_nsfw_filter import is_explicit, count_hits
    is_explicit("nội dung chương...")   # -> True/False
    count_hits("...")                    # -> số từ khoá explicit khớp

Tolerant to font-corrupted (missing-diacritic) text; no model/GPU needed.
"""
from .lexicon import (
    DEFAULT_HIT_THRESHOLD,
    SAFE_DEACCENT,
    ACCENT,
    deaccent,
    count_hits,
    is_explicit,
)
from .normalize import normalize
from .thin import is_thin, DEFAULT_MIN_CHARS

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_HIT_THRESHOLD",
    "SAFE_DEACCENT",
    "ACCENT",
    "deaccent",
    "count_hits",
    "is_explicit",
    "normalize",
    "is_thin",
    "DEFAULT_MIN_CHARS",
    "__version__",
]
