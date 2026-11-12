# Poker Schmoker: Live Table Assistant — Design

## Intent

Build a Windows desktop companion for a six-handed No-Limit Hold'em table. Its primary flow is observing the active table, detecting when the hero can act, tracking opponents across hands, and showing a reasoned action recommendation during the decision window. Post-hand review is secondary.

## Scope and staged delivery

The full product comprises: screen capture, vision/OCR, table-state tracking, persistent player statistics, probabilistic ranges, equity/EV analysis, a strategy engine, and a visible user-controlled overlay. It never presses a poker-client button, attempts to conceal itself from the client, or bypasses protections.

**Initial vertical slice:** screen-state detector, an explicit observation model, pure poker mathematics, a Windows capture CLI, and tests against both synthetic observations and local sample screenshots. An incomplete observation must produce `unknown`, not a fabricated recommendation. Hand history, player profiling, and an advanced strategy engine follow as separate increments.

## Inputs and confidence

- Source: user-selected window or region; repeated screenshots, without poker-client APIs or code injection.
- UI reference: three screenshots provided November 11, 2026. Two show hero action panels, one lacks the panel. Their sizes differ: 799×677, 807×683, 710×575.
- Source screenshots are **local test inputs only**. Do not commit them to this public repository: they include names and balances.
- Vision distinguishes `hero_turn`, `not_hero_turn`, and `unknown`, with evidence and confidence. A bottom action panel containing a fold button plus call/check or raise evidence is a hero-turn cue. Missing panel is not by itself definitive without the calibrated window bounds; false positives are worse than abstention.
- Hero cards, board cards, amounts, and nicknames may be individually unknown. Interpret OCR as uncertain evidence, validate card uniqueness and monetary units, and never silently coerce unreadable values into zero.

## Architecture

Python 3.11+, package `poker_schmoker`:

1. `model`: immutable cards, actions, observations and confidence.
2. `poker`: 5-card evaluator, best-of-seven evaluator, exact hand comparison and pot-odds arithmetic.
3. `vision`: image preprocessing and UI regions scaled from reference proportions; separate turn detector and OCR adapters.
4. `capture`: Windows screen capture and local-image replay behind a single frame-source protocol.
5. `history`: eventual SQLite action log and player aggregates with explicit hand/session identifiers.
6. `strategy`: eventual ranges, equity, EV, sizing and decision explanation; abstain until inputs are reliable.
7. `app`: user-facing diagnostics first; visual overlay later.

No external AI call is required to interpret a frame. Statistical profiles are only based on hands actually observed; every percentage reports its sample size.

## Milestone 1 acceptance

- Given normalized snapshots of the three samples, classify the two visible action panels as hero-turn candidates and the third as no visible hero action panel; do not infer a board card from the third screenshot's card back.
- Correctly evaluate hand rankings, ties, kickers, and best five out of seven using deterministic tests.
- Pot odds computation returns a bounded probability for valid inputs and refuses invalid inputs.
- Frame analysis returns explicit unknowns rather than invented cards or amounts when OCR fails.
- A CLI reads a local image and prints state/confidence/evidence; a separate Windows live mode periodically captures a selected screen region.
- No automated table inputs or claims of a complete GTO solver in this milestone.

## Risks and mitigations

- Screenshots vary with table size and UI skin: scale normalized regions and require a calibrated layout; retain unknown states otherwise.
- Temporary animation / occlusion: require multiple consecutive consistent detections before notifying.
- 6-max seats may be empty or sit-out: keep seat occupancy separate from action history.
- OCR errors on amounts can distort strategy: preserve raw text/confidence and gate numerical advice on validation.
- Opponent profiles from tiny samples are unstable: show sample sizes and use uncertainty-aware estimates.

## Follow-on increments

1. Region calibration, robust rank/suit recognition, board and player extraction with screenshot fixtures covering all ranks.
2. Transition-based hand tracker and session replay with SQLite persistence.
3. Range inference and Monte Carlo equity; measured latency and confidence gates.
4. Validated strategy recommendations and Windows overlay; separate offline-vs-live acceptance tests.
