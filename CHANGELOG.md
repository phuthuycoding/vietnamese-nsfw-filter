# Changelog

## 0.2.0

### Fixed (false positives on clean text)
- **`tinh dịch` (semen)** moved from the de-accent layer to the diacritic layer — its
  de-accented form `tinh dich` collided with **`tình địch` (love rival)**, a very common
  romance word. Real `tinh dịch` is still detected; `tình địch` no longer false-flags.
- **`khoái lạc`** removed from the default layer (→ opt-in `WEAK`). It mostly means
  ordinary "joy/pleasure" and also appears in proper names (e.g. the wuxia title
  *Khoái Lạc Vương*), causing heavy false positives on non-explicit text.
- **`bach dich`** removed from the default layer (→ opt-in `WEAK`). It collides with the
  common cultivation-novel character name **`Bạch Dịch`**.

### Added
- New explicit act terms (curated from
  [blue-eyes-vn/vietnamese-offensive-words](https://github.com/blue-eyes-vn/vietnamese-offensive-words),
  filtered for de-accent collisions): `banh háng`, `xéo háng`, `đút đít`, `húp sò`.
- Opt-in `WEAK` additions: `khoái lạc`, `bạch dịch`, `chổng mông`, `xoạc`.
- Regression tests for the homograph/proper-name collisions above.
- README: documented that **asterisk-self-censored text (`dương v*t`, `tiểu huy*t`) is not
  handled** — sources mask violence/everyday words too, so `*` is not an NSFW signal;
  restore the text before running the lexicon.

## 0.1.1

- Initial public release: lexicon-based NSFW/explicit detector, font-corruption tolerant,
  de-accent + diacritic matching layers, opt-in WEAK layer, thin-content filter.
