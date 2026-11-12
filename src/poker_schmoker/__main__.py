"""Local image replay and Windows screen observer command-line entry point."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

from PIL import Image

from .cards import CardObservation, observe_cards
from .observer import TurnDebouncer
from .streets import StreetTracker
from .vision import detect_action_panel


def _bbox(value: str) -> tuple[int, int, int, int]:
    try:
        values = tuple(int(item.strip()) for item in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("bbox must be left,top,right,bottom") from exc
    if len(values) != 4 or values[0] >= values[2] or values[1] >= values[3]:
        raise argparse.ArgumentTypeError("bbox must contain a nonempty rectangle")
    return values  # type: ignore[return-value]


def _card_code(card) -> str | None:
    return None if card is None else "23456789TJQKA"[card.rank - 2] + card.suit


def _cards_json(observation: CardObservation) -> dict:
    return {
        "hero": [_card_code(card) for card in observation.hero_cards],
        "board": [_card_code(card) for card in observation.board_cards],
        "street": observation.street,
        "complete": observation.complete,
    }


def _observation_json(observation, cards: CardObservation) -> str:
    result = {
        "state": observation.state,
        "confidence": observation.confidence,
        "evidence": list(observation.evidence),
        "cards": _cards_json(cards),
    }
    return json.dumps(result, ensure_ascii=False)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="poker_schmoker")
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("inspect", help="Analyze a saved table screenshot")
    inspect.add_argument("image", type=Path)
    inspect.add_argument("--bbox", type=_bbox, help="Optional table rectangle inside a desktop screenshot")
    watch = commands.add_parser("watch", help="Observe a calibrated Windows table window")
    watch.add_argument("--bbox", type=_bbox, required=True, help="left,top,right,bottom for the Pokerdom window")
    watch.add_argument("--interval", type=float, default=.5, help="capture interval in seconds")
    args = parser.parse_args(argv)

    if args.command == "inspect":
        try:
            with Image.open(args.image) as frame:
                if args.bbox is not None:
                    left, top, right, bottom = args.bbox
                    if left < 0 or top < 0 or right > frame.width or bottom > frame.height:
                        raise ValueError("bbox is outside screenshot bounds")
                    frame = frame.crop(args.bbox)
                result = detect_action_panel(frame)
                cards = observe_cards(frame)
        except (OSError, ValueError) as exc:
            print(f"Could not read screenshot: {exc}", file=sys.stderr)
            return 2
        print(_observation_json(result, cards))
        return 0

    if sys.platform != "win32":
        print("Live screen capture is currently supported on Windows only.", file=sys.stderr)
        return 2
    if args.interval <= 0:
        print("--interval must be positive", file=sys.stderr)
        return 2

    from PIL import ImageGrab

    debouncer = TurnDebouncer(required=2)
    streets = StreetTracker()
    print("Watching the selected window bounds. Press Ctrl+C to stop.", file=sys.stderr)
    try:
        while True:
            frame = ImageGrab.grab(bbox=args.bbox)
            observed = detect_action_panel(frame)
            cards = observe_cards(frame)
            current_street = streets.push(cards)
            if current_street is not None:
                print(json.dumps({
                    "event": "street_changed",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "cards": _cards_json(cards),
                }, ensure_ascii=False), flush=True)
            if debouncer.push(observed):
                event = {
                    "event": "hero_turn_detected",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "confidence": observed.confidence,
                    "evidence": list(observed.evidence),
                    "cards": _cards_json(cards),
                }
                print(json.dumps(event, ensure_ascii=False), flush=True)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
