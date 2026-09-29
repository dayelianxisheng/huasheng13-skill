#!/usr/bin/env python3
"""Minimal self-check for the method-card index."""

from search_cards import load_cards, search


cards = load_cards()
assert len(cards) == 442
assert len({card["id"] for card in cards}) == len(cards)
matches = search(cards, "增长率 比较", "资料分析", 3)
assert matches and all("资料分析" in match["module"] for match in matches)
assert all("id" in match and "need_review" in match for match in matches)
print("ok")
