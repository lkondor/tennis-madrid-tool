import json
from datetime import datetime
from pathlib import Path


DATA_PATH = Path("data/live/matches.json")


class Match:
    def __init__(self, player1, player2, court, date):
        self.player1 = player1
        self.player2 = player2
        self.court = court
        self.date = date


def load_all_matches():
    if not DATA_PATH.exists():
        return []

    with open(DATA_PATH) as f:
        raw = json.load(f)

    matches = []
    for m in raw:
        matches.append(
            Match(
                m["player1"],
                m["player2"],
                m["court"],
                m["date"]
            )
        )
    return matches


def get_available_dates(matches):
    return sorted(list(set(m.date for m in matches)))


def get_matches_by_date(selected_date):
    matches = load_all_matches()
    return [m for m in matches if m.date == selected_date]
