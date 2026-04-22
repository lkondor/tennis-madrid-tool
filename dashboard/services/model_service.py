import json
from pathlib import Path


PLAYERS_PATH = Path("data/live/players.json")


def load_players():
    if not PLAYERS_PATH.exists():
        return {}
    with open(PLAYERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def win_prob(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))


def court_factor(court: str):
    c = court.lower()
    if "court 4" in c:
        return 1.08
    if "manolo" in c:
        return 1.02
    if "arantxa" in c:
        return 1.01
    return 1.0


def run_prediction(match):
    players = load_players()

    a = players.get(match.player1.lower(), {})
    b = players.get(match.player2.lower(), {})

    elo_a = a.get("elo_clay", 1800)
    elo_b = b.get("elo_clay", 1800)

    ace_rate_a = a.get("ace_rate_clay_3y", 5.5)
    ace_rate_b = b.get("ace_rate_clay_3y", 5.5)

    ace_allowed_a = a.get("ace_allowed_clay_3y", 5.5)
    ace_allowed_b = b.get("ace_allowed_clay_3y", 5.5)

    break_rate_a = a.get("break_rate_clay_3y", 2.0)
    break_rate_b = b.get("break_rate_clay_3y", 2.0)

    break_allowed_a = a.get("break_allowed_clay_3y", 2.0)
    break_allowed_b = b.get("break_allowed_clay_3y", 2.0)

    p_a = win_prob(elo_a, elo_b)
    p_b = 1 - p_a

    c_factor = court_factor(match.court)
    madrid_factor = 1.15
    match_length = 1.08 + (1 - abs(p_a - 0.5)) * 0.5

    aces_a = round(((ace_rate_a + ace_allowed_b) / 2) * c_factor * madrid_factor * match_length, 1)
    aces_b = round(((ace_rate_b + ace_allowed_a) / 2) * c_factor * madrid_factor * match_length, 1)

    breaks_a = round(((break_rate_a + break_allowed_b) / 2) * (1.12 - (c_factor - 1) * 0.5), 1)
    breaks_b = round(((break_rate_b + break_allowed_a) / 2) * (1.12 - (c_factor - 1) * 0.5), 1)

    result = {
        "playerA": {"aces": aces_a, "breaks": breaks_a},
        "playerB": {"aces": aces_b, "breaks": breaks_b},
        "totals": {
            "aces": round(aces_a + aces_b, 1),
            "breaks": round(breaks_a + breaks_b, 1)
        }
    }

    context = {
        "elo_a": elo_a,
        "elo_b": elo_b,
        "win_prob_a": round(p_a, 3),
        "win_prob_b": round(p_b, 3),
        "court_factor": c_factor,
        "madrid_factor": madrid_factor,
        "match_length": round(match_length, 2)
    }

    return result, context
