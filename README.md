# Poker Schmoker

Windows-oriented observation and study tools for six-handed No-Limit Texas Hold'em.

## Status

**Early milestones**: recognizes the action-button panel, calibrated card faces and known rank/suit glyphs, debounces turn events, detects community-card street changes, and evaluates poker hands and pot odds. It does **not** yet track players across hands, calculate equity against opponents, or recommend bets. Do not interpret a detected panel as a validated optimal poker move.

The tool does not click controls in a poker client or attempt to bypass client protections. Use of real-time assistance may violate the rules of an online poker service.

## Setup (Windows)

Install Python 3.11 or newer, then in PowerShell in the project folder:

```powershell
py -m pip install -e .
py -m unittest discover -s tests -v
```

## Inspect a screenshot

```powershell
py -m poker_schmoker inspect C:\Users\You\Pictures\table.png
```

Output is JSON with `state` (`hero_turn`, `not_hero_turn`, or `unknown`), `confidence`, the observed visual cues and `cards` (`hero`, `board`, `street`, `complete`). A missing card rank or suit is `null`, and downstream decisions must not rely on an incomplete observation.

If the screenshot contains the entire desktop, use `--bbox left,top,right,bottom` to isolate the table window before analysis. The coordinates are relative to the screenshot.

## Observe the screen

Use the Pokerdom window's **outer rectangle** in screen coordinates. For example, if it begins at `(100, 100)` and is `800 × 680` pixels:

```powershell
py -m poker_schmoker watch --bbox 100,100,900,780 --interval 0.5
```

When two successive frames contain the calibrated action panel, the command prints one `hero_turn_detected` event with recognised cards. It also emits `street_changed` as a consistent board progresses. It stops with Ctrl+C. Keep the complete table window visible; resizing, overlapping windows, themes and animations can invalidate detection. No active game integration has been verified on this Linux build host.

The built-in card glyph dictionary currently covers ranks `2, 4, 5, 6, 7, 9, 10, K, A` and all four suits, from the supplied PokerDom skin. Ranks `3, 8, J, Q` and other skins are **not covered**; recognition should return `null` for unmatched glyphs. This is a bounded template recognizer, not general card OCR.

## Screenshots and privacy

`local_samples/` is excluded from git. Keep local Pokerdom screenshots there; they may contain player names and balances. The three user-provided screenshots were tested locally but are not part of this public repository.

## Roadmap

Next: complete the card glyph alphabet, bet/stack OCR, robust hand ID/action transitions, SQLite player profiles, then range-aware equity and strategy with a separate Windows overlay. See `docs/superpowers/specs/2026-11-11-live-table-assistant-design.md`.
