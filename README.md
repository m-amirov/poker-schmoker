# Poker Schmoker

Windows-oriented observation and study tools for six-handed No-Limit Texas Hold'em.

## Status

**Milestone 1 only**: recognizes the action-button panel on a calibrated Pokerdom table screenshot, debounces turn events, and evaluates poker hands and pot odds. It does **not** yet recognize cards, track players across hands, calculate equity against opponents, or recommend bets. Do not interpret a detected panel as a validated optimal poker move.

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

Output is JSON with `state` (`hero_turn`, `not_hero_turn`, or `unknown`), `confidence`, and the observed visual cues. Any unrelated or incomplete image must be treated as `unknown`.

If the screenshot contains the entire desktop, use `--bbox left,top,right,bottom` to isolate the table window before analysis. The coordinates are relative to the screenshot.

## Observe the screen

Use the Pokerdom window's **outer rectangle** in screen coordinates. For example, if it begins at `(100, 100)` and is `800 × 680` pixels:

```powershell
py -m poker_schmoker watch --bbox 100,100,900,780 --interval 0.5
```

When two successive frames contain the calibrated action panel, the command prints one `hero_turn_detected` event. It stops with Ctrl+C. Keep the complete table window visible; resizing, overlapping windows, themes and animations can invalidate detection. No active game integration has been verified on this Linux build host.

## Screenshots and privacy

`local_samples/` is excluded from git. Keep local Pokerdom screenshots there; they may contain player names and balances. The three user-provided screenshots were tested locally but are not part of this public repository.

## Roadmap

Next: card/board OCR, bet/stack OCR, explicit hand state transitions, SQLite player profiles, then range-aware equity and strategy with a separate Windows overlay. See `docs/superpowers/specs/2026-11-11-live-table-assistant-design.md`.
