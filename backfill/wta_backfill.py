import json
from collections import defaultdict
from pathlib import Path

import requests
from bs4 import BeautifulSoup


WTA_MATCHES_PATH = Path("data/live/wta_matches_history.json")


def load_wta_match_history():
    if not WTA_MATCHES_PATH.exists():
        return []
    with open(WTA_MATCHES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def aggregate_wta_players_from_matches():
    matches = load_wta_match_history()

    players = defaultdict(lambda: {
        "tour": "WTA",
        "aces": 0,
        "service_games_played": 0,
        "breaks_made": 0,
        "return_games_played": 0,
        "matches": 0,
        "madrid_matches": 0,
        "madrid_aces": 0,
        "madrid_breaks": 0,
        "stats_by_year_clay": {
            "2023": {"aces": 0, "service_games_played": 0, "breaks_made": 0, "return_games_played": 0, "matches": 0},
            "2024": {"aces": 0, "service_games_played": 0, "breaks_made": 0, "return_games_played": 0, "matches": 0},
            "2025": {"aces": 0, "service_games_played": 0, "breaks_made": 0, "return_games_played": 0, "matches": 0},
            "2026": {"aces": 0, "service_games_played": 0, "breaks_made": 0, "return_games_played": 0, "matches": 0},
        }
    })

    for m in matches:
        if m.get("surface", "").lower() != "clay":
            continue

        year = str(m["date"][:4])
        if year not in ["2023", "2024", "2025", "2026"]:
            continue

        p1 = m["player1"].lower().strip()
        p2 = m["player2"].lower().strip()

        for player_key, side in [(p1, "p1"), (p2, "p2")]:
            aces = m.get(f"aces_{side}", 0)
            sgp = m.get(f"service_games_played_{side}", 0)
            breaks = m.get(f"breaks_made_{side}", 0)
            rgp = m.get(f"return_games_played_{side}", 0)

            players[player_key]["aces"] += aces
            players[player_key]["service_games_played"] += sgp
            players[player_key]["breaks_made"] += breaks
            players[player_key]["return_games_played"] += rgp
            players[player_key]["matches"] += 1

            players[player_key]["stats_by_year_clay"][year]["aces"] += aces
            players[player_key]["stats_by_year_clay"][year]["service_games_played"] += sgp
            players[player_key]["stats_by_year_clay"][year]["breaks_made"] += breaks
            players[player_key]["stats_by_year_clay"][year]["return_games_played"] += rgp
            players[player_key]["stats_by_year_clay"][year]["matches"] += 1

            if m.get("tournament", "").lower() == "madrid":
                players[player_key]["madrid_matches"] += 1
                players[player_key]["madrid_aces"] += aces
                players[player_key]["madrid_breaks"] += breaks

    return dict(players)
