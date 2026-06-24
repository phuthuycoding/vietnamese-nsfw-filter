# vietnamese-nsfw-filter

Lexicon-based **NSFW / explicit text detector for Vietnamese**. Counts the density of
explicit keywords — **no model, no GPU, pure stdlib**. Built for moderating large
corpora of Vietnamese web-novel / UGC text where you need to flag pornographic content
for removal or age-gating.

Two things make it work on **real, messy** Vietnamese data:

- **Font-corruption tolerant** — scraped text often loses diacritics
  (`"dương vật"` → `"duong vat"` / `"duơng v t"`). A de-accented matching layer still
  catches these.
- **No homograph false positives** — naively de-accenting Vietnamese collides badly
  (`"dâm đãng"` lewd vs `"đảm đang"` virtuous; `"bắn tinh"` vs `"bản tính"`;
  `"nứng"` vs `"nung nấu"`). Those terms are matched **with diacritics** instead.

## Install

```bash
pip install vietnamese-nsfw-filter
```

## Usage

```python
from vietnamese_nsfw_filter import is_explicit, count_hits

is_explicit("Hắn đút dương vật vào âm đạo, làm tình mãnh liệt...")   # True
is_explicit("Hôm nay trời đẹp, cả nhà ra đồng gặt lúa.")            # False

count_hits("...")        # number of explicit keywords matched
is_explicit(text, threshold=5)   # custom sensitivity (default 3)
```

Helpers for noisy scraped text:

```python
from vietnamese_nsfw_filter import normalize, is_thin, deaccent

normalize(raw_text)      # NFC + whitespace cleanup (idempotent, no spell-fix)
is_thin(text)            # (True, "boilerplate:...") for login-gate/paywall/too-short
deaccent("Dương Vật")    # "duong vat"
```

## How it works

1. Split nothing — you decide the unit (a chapter, a chunk, a comment).
2. `count_hits(text)` matches two keyword sets:
   - `SAFE_DEACCENT` — clinical Sino-Vietnamese terms, matched on **de-accented** text
     (so corrupted fonts still hit).
   - `ACCENT` — homograph-prone terms + native slang, matched **with diacritics**
     (so clean words aren't flagged).
3. `is_explicit(text, threshold)` = `count_hits(text) >= threshold`.

For **document/story-level** decisions, count what fraction of units are explicit and
threshold on density (e.g. a story with ≥30% explicit chapters → flag) — far more robust
than any single chapter.

## Tuning the lexicon

The keyword lists are plain Python lists you can extend:

```python
import vietnamese_nsfw_filter.lexicon as lex
lex.SAFE_DEACCENT  # de-accented terms (must NOT collide with normal words)
lex.ACCENT         # terms kept with diacritics (homograph-prone + slang)
```

When adding a term: if its de-accented form could be a normal Vietnamese word, put it in
`ACCENT` (with diacritics); otherwise `SAFE_DEACCENT`.

## Scope & limitations

- Targets **explicit sexual content** (the highest-signal, most-requested NSFW category).
- Lexicon/density catches *depiction* (porn) well; it can **miss euphemism-heavy** prose
  and is **not** a substitute for human review on removal decisions — use it as a
  high-recall first filter, then review/escalate the flagged set.

## ⚠️ Content notice

This package necessarily contains a list of explicit Vietnamese terms (in
`src/vietnamese_nsfw_filter/lexicon.py`) for **detection purposes only**.

## Development

```bash
pip install -e ".[test]"
pytest
```

## License

MIT © phuthuycoding
