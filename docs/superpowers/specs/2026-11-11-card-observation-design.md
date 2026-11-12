# Poker Schmoker: Card Observation Increment

## Intent

Extend the approved live table observer to recognise face-up hero and community cards and identify flop/turn/river transitions. The supplied frames from one Pokerdom hand are the concrete validation sequence: hero `Ts 5c`, flop `9c 6h Ac`, turn `2s`, river `4c`.

## Approaches

- OCR-only: reject for card rank recognition because repeated Tesseract tests misread the decorative PokerDom card font (`9` as `J`, `6` as `o`, `10` as `1U`).
- Generic deep-learning detector: viable later, but adds a model dependency and training data we do not have.
- **Selected for this increment:** geometry-based card-face detection plus compact glyph masks learned from user-provided cards. Works on a calibrated client skin without publishing account names or balances. Unknown glyphs remain unknown.

## Design

1. Locate near-white rectangular components with the expected card aspect ratio in normalized hero/board regions. The six supplied screens use cards that appear as 56×78 light rectangles separated by dark gaps; support modest scaling.
2. Read only rank and suit glyphs at normalized offsets inside each face. Compare binary masks with fixed templates and require both an absolute match threshold and separation from the second-best match.
3. Ship templates as text-only extracted glyph masks; do not ship screenshots or player names.
4. Return a structured `CardObservation` with per-card `Card | None`; do not invent missing ranks or suits. Supported board cardinalities: zero (preflop), 3 (flop), 4 (turn), 5 (river). Unsupported card counts become unknown street.
5. Provide a pure `StreetTracker` that emits transitions from flop to turn to river only when consistent observations arrive. It must not assume two separately observed tables are the same hand.
6. Extend `inspect` JSON with `cards` fields while retaining existing `state/confidence/evidence` for backwards compatibility.

## Bounds and acceptance

- Exactly recognise cards from the three newly supplied postflop frames; also recognise visible preflop cards covered by the available glyph alphabet.
- Handle missing glyphs and missing faces conservatively (`null` instead of a guessed card).
- Reject impossible duplicate face-up cards across hero and board.
- Unit tests use synthetic frames and text-mask data; source screenshots remain outside GitHub.
- This increment still does not recognise stacks, bets, player names, or deliver live strategic recommendations. It advances the approved roadmap without claiming the end product is ready.

## Risk

The alphabet is incomplete (`3`, `8`, `J`, `Q` have no reference image) and the recognizer is skin-specific. Missing ranks must be surfaced as unknown; collect more screenshot examples before expanding. Text-mask data is a deliberately bounded classifier, not universal OCR.
