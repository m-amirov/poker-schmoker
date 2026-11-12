# Card Observation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Detect hero and board cards from calibrated Pokerdom screenshots and report street transitions without inventing unknown cards.

**Architecture:** Connected light-region components detect cards; binary rank/suit masks classify glyphs. A pure observation model and a street tracker sit above this recognizer; the screenshot CLI reports them alongside current action-panel state.

**Tech Stack:** Python 3.11+, Pillow, stdlib, unittest; text-only glyph mask resource.

**Spec:** `docs/superpowers/specs/2026-11-11-card-observation-design.md`

## Global Constraints

- Do not publish the user's original screenshots, player names or balances.
- Unknown rank/suit stays `None`; no fictional strategic output.
- Backward-compatible `inspect` JSON fields `state/confidence/evidence`.
- Calibrated skin only, no claims of universal OCR or ready-to-use RTA.

## Review Focus

1. Face-down animation card: must not appear as a community card.
2. Incomplete light components: no ghost card.
3. Hero/board duplicate: reject impossible observation.
4. Unsupported rank: report unknown rather than nearest known rank.
5. Board out of 0/3/4/5 card count: street unknown, no inferred progression.

---

### Task 1: Face Rectangles

**Files:** Create `src/poker_schmoker/cards.py`; Test `tests/test_cards.py`.

**Interfaces:** `detect_card_boxes(image: Image.Image, zone: Literal['hero','board']) -> tuple[CardBox, ...]`; `CardBox` fields `left, top, right, bottom` and `.crop(image)`.

- [ ] Write synthetic image tests with 2 hero and 3/4/5 board white 56×78 cards, dark face-down card and torn/partial card.
- [ ] Run `PYTHONPATH=src python -m unittest discover -s tests -p test_cards.py -v`; expected missing module error.
- [ ] Implement 4-connected bright-components, aspect/area gates and normalized screen zones.
- [ ] Re-run focused and full suite; expected PASS.
- [ ] Commit `feat: locate face-up cards in table regions`.

### Task 2: Glyph Recognition

**Files:** Add `src/poker_schmoker/data/card_glyphs.json`; Modify `src/poker_schmoker/cards.py` and `pyproject.toml`; Test `tests/test_card_glyphs.py`.

**Interfaces:** `read_card(image: Image.Image, box: CardBox) -> Card | None`; `observe_cards(image: Image.Image) -> CardObservation` with `hero_cards`, `board_cards`, `street`, and `complete`.

- [ ] Write test for known card glyph arrays, unknown glyph, suit differentiation, cross-zone duplicates and valid street cardinalities.
- [ ] Run focused test; expected missing `read_card` import.
- [ ] Generate text masks only from card crops, not whole screenshots; ship as `data/card_glyphs.json`.
- [ ] Implement bounded glyph classifier, duplicate checks and `CardObservation`.
- [ ] Run focused and full suite; expected PASS.
- [ ] Verify the six local screenshots, listing any mismatches; do not commit screenshots.
- [ ] Commit `feat: recognise calibrated hero and board glyphs`.

### Task 3: Street Progression and CLI

**Files:** Create `src/poker_schmoker/streets.py`; Modify `src/poker_schmoker/__main__.py`, `README.md`; Test `tests/test_streets.py`, `tests/test_cli.py`.

**Interfaces:** `StreetTracker.push(observation: CardObservation) -> str | None`, returning new street only when a valid board expansion is observed in the same hero hand. CLI `inspect` includes `cards.hero`, `cards.board`, `cards.street`, `cards.complete`.

- [ ] Write transitions 3→4→5 and unknown/nonmonotone reset tests; CLI JSON backward-compatibility test.
- [ ] Run focused tests; expected missing tracker or cards keys.
- [ ] Implement tracker and CLI output; document bounded known-rank alphabet.
- [ ] Run full suite, local frame verification, compile and diff whitespace check; expected PASS.
- [ ] Commit `feat: report card observations and street transitions`.

## Self-review

- Each task provides an independently testable interface consumed by the next.
- Synthetic tests cover card geometry; local screenshots provide additional non-published integration evidence.
- Deliberate limitation: no player history or live action selection in this increment.
