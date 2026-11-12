# Milestone 1 Live Observation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a runnable, testable Windows-oriented screenshot observer and basic Hold'em arithmetic without pretending incomplete observations yield optimal poker decisions.

**Architecture:** A small Python package separates card evaluation, screenshot-derived action-panel cues, and repeatable live frame capture. Input models represent unknowns explicitly; the CLI supports file replay before a Windows live integration.

**Tech Stack:** Python 3.11+, standard library, Pillow; unittest; optional Tesseract for later OCR extensions.

**Spec:** `docs/superpowers/specs/2026-11-11-live-table-assistant-design.md`

## Global Constraints

- Windows desktop target, No-Limit Hold'em six-max.
- Local-only capture, no automated client button interaction or bypass of client protections.
- The public repository must not contain source screenshots with account names or balances.
- Unknown card/amount/turn observations remain unknown; no fabricated recommendation.
- Milestone 1 is the live observation foundation, not a complete strategy solver.

## Review Focus

1. Screenshot of unrelated desktop: observer must not emit a hero-turn positive.
2. OCR failure: no invented card, stake, or player information appears.
3. Same UI at different resolutions: normalized feature regions still detect action bars.
4. Duplicate card and invalid card code: poker model refuses impossible hands.
5. Negative/zero call amount: pot-odds calculation rejects invalid values.

---

### Task 1: Poker Value Types and Hand Evaluation

**Files:** Create `src/poker_schmoker/model.py`, `src/poker_schmoker/poker.py`, `src/poker_schmoker/__init__.py`; Test `tests/test_poker.py`.

**Interfaces:** `Card.parse(code: str) -> Card`; `hand_rank(cards: Sequence[Card]) -> tuple[int, ...]` (exactly five); `best_hand_rank(cards: Sequence[Card]) -> tuple[int, ...]` (five to seven); `pot_odds(call_amount: Decimal, pot_before_call: Decimal) -> Decimal`.

- [ ] Write tests for wheel straight, flush vs straight, two-pair kicker, seven-card best selection, duplicate rejection, and pot odds `Decimal('2')` into pot `Decimal('6')` => `Decimal('0.25')`.
- [ ] Run `python -m unittest discover -s tests -p 'test_poker.py' -v`; expected missing-import error.
- [ ] Implement minimal immutable `Card`, parsing/validation, seven-card evaluator and odds function.
- [ ] Run same command; expected all PASS.
- [ ] Commit `feat: add hold'em value types and exact hand evaluation`.

### Task 2: Action Panel Detector

**Files:** Create `src/poker_schmoker/vision.py`; Test `tests/test_vision.py`.

**Interfaces:** `detect_action_panel(image: PIL.Image.Image) -> ActionPanelObservation` with `state: Literal['hero_turn','not_hero_turn','unknown']`, `confidence: float`, `evidence: tuple[str, ...]`. The detector operates on normalized bottom-bar relative regions; it checks independent color-coded button cues, not text OCR. A region lacking enough panel evidence is `not_hero_turn` only if a calibrated full-window frame is supplied; unrelated images are `unknown`.

- [ ] Write tests with synthetic bottom-bar color cues at two image sizes, grayscale/blank image abstention, and a visible action bar with no call button but check present.
- [ ] Run `python -m unittest discover -s tests -p 'test_vision.py' -v`; expected missing-import error.
- [ ] Implement normalized-region evidence and confidence threshold. Use integer HSV/RGB predicates only where deterministic; avoid loading source screenshots as fixtures.
- [ ] Run same command; expected all PASS.
- [ ] Commit `feat: detect live hero action panels from screenshots`.

### Task 3: Frame Debouncing and Local Replay CLI

**Files:** Create `src/poker_schmoker/observer.py`, `src/poker_schmoker/__main__.py`, `README.md`, `pyproject.toml`; Test `tests/test_observer.py`.

**Interfaces:** `TurnDebouncer(required: int = 2).push(observation: ActionPanelObservation) -> bool`, returning True only on first stable transition to hero-turn. `python -m poker_schmoker inspect path.png` emits JSON with state/confidence/evidence; `python -m poker_schmoker watch --interval 0.5` uses Pillow `ImageGrab` only on Windows and emits events.

- [ ] Write tests for one-frame false positive, two-frame transition, repeated alert suppression, and unknown reset.
- [ ] Run `python -m unittest discover -s tests -p 'test_observer.py' -v`; expected missing-import error.
- [ ] Implement debouncer, replay CLI, Windows capture (non-Windows should report unavailable), and instructions.
- [ ] Run same command; expected all PASS.
- [ ] Commit `feat: add replay CLI and debounced Windows screen observer`.

### Task 4: Sample Verification and Public Repo Hygiene

**Files:** Modify `README.md`, create `.gitignore`, add `tests/test_cli.py`.

**Interfaces:** Screenshot diagnostics never print opponent name/card information they cannot confidently identify; only panel state/confidence/evidence are emitted in Milestone 1.

- [ ] Write CLI integration test for missing file and no-action synthetic frame, plus assertion that repository excludes local screenshot paths.
- [ ] Run `python -m unittest discover -s tests -p 'test_cli.py' -v`; expected missing test or failing CLI contract.
- [ ] Implement safe error handling and ignored local fixtures.
- [ ] Run `python -m unittest discover -s tests -v`; expected all PASS.
- [ ] Run the `inspect` command on all three local screenshots (not committed), record observed states and any mismatch transparently.
- [ ] Commit `test: verify screenshot observer and document its limits`.

## Self-review

- The plan implements the **first** slice only. Hand history, player memory, equity-range analysis, and live recommendations are explicitly follow-on milestones from the spec, not silently dropped requirements.
- Interfaces use stable imports and no screenshot-specific identifiers.
- Tests cover every Review Focus item, plus debouncing for animations.
