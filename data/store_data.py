# -*- coding: utf-8 -*-
"""🛒 Free Fire Do'koni - vaucher va pass turlari."""

STORE_ITEMS = [
    {
        "key": "weekly",
        "label": "🎫 Xaftalik vaucher",
        "price": 18000,
        "desc": "Free Fire Xaftalik (haftalik) vaucher.",
    },
    {
        "key": "monthly",
        "label": "🎫 Oylik vaucher",
        "price": 79000,
        "desc": "Free Fire Oylik vaucher.",
    },
    {
        "key": "booyah",
        "label": "🎫 Booyah Pass",
        "price": 60000,
        "desc": "Booyah Pass.",
    },
    {
        "key": "levelup",
        "label": "🎫 Level Up Pass",
        "price": 70000,
        "desc": "Level Up Pass — 1250 almaz.",
    },
]


def find_store_item(key: str):
    for item in STORE_ITEMS:
        if item["key"] == key:
            return item
    return None
