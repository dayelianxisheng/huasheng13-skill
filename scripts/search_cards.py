#!/usr/bin/env python3
"""Search or retrieve structured 公考 method cards using only the stdlib."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


CARDS = Path(__file__).resolve().parents[1] / "references" / "method-cards" / "all_cards.jsonl"
HIGH_FIELDS = (
    "id",
    "module",
    "question_type",
    "sub_type",
    "method_name",
    "aliases",
    "tags",
    "trigger_conditions",
)
BROAD_FIELDS = HIGH_FIELDS + (
    "anti_conditions",
    "required_inputs",
    "steps",
    "formulas",
    "examples",
    "pitfalls",
)


def stringify(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{stringify(k)} {stringify(v)}" for k, v in value.items())
    if isinstance(value, list):
        return " ".join(map(stringify, value))
    return "" if value is None else str(value)


def load_cards() -> list[dict[str, Any]]:
    with CARDS.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def rank(card: dict[str, Any]) -> int:
    priority = card.get("solver_priority")
    return priority.get("rank", 999) if isinstance(priority, dict) else 999


def search(cards: list[dict[str, Any]], query: str, module: str | None, limit: int) -> list[dict[str, Any]]:
    terms = [term.casefold() for term in query.split() if term]
    scored: list[tuple[int, dict[str, Any]]] = []
    for card in cards:
        if module and module not in str(card.get("module", "")):
            continue
        high = " ".join(stringify(card.get(key)) for key in HIGH_FIELDS).casefold()
        broad = " ".join(stringify(card.get(key)) for key in BROAD_FIELDS).casefold()
        score = sum(high.count(term) * 5 + broad.count(term) for term in terms)
        if score:
            scored.append((score, card))
    scored.sort(key=lambda item: (-item[0], bool(item[1].get("need_review")), rank(item[1]), item[1].get("id", "")))
    return [
        {
            "score": score,
            "id": card.get("id"),
            "module": card.get("module"),
            "question_type": card.get("question_type"),
            "sub_type": card.get("sub_type"),
            "method_name": card.get("method_name"),
            "trigger_conditions": card.get("trigger_conditions", []),
            "anti_conditions": card.get("anti_conditions", []),
            "required_inputs": card.get("required_inputs", []),
            "solver_priority": card.get("solver_priority"),
            "need_review": card.get("need_review", False),
        }
        for score, card in scored[:limit]
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Search 公考 method cards")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("query", nargs="?", help="Space-separated search terms")
    group.add_argument("--id", dest="method_id", help="Return one complete method card")
    parser.add_argument("--module", help="Filter by module name or prefix")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    cards = load_cards()
    if args.method_id:
        result = next((card for card in cards if card.get("id") == args.method_id), None)
    else:
        result = search(cards, args.query, args.module, max(args.limit, 0))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
