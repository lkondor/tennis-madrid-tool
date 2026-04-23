import json
from pathlib import Path

from backfill.similarity import find_similar_players
from backfill.weather import ace_weather_factor, break_weather_factor


PLAYERS_PATH = Path("data/live/players.json")
WEATHER_PATH = Path("data/live/weather.json")


def load_players():
    if not PLAYERS_PATH.exists():
        return {}
    with open(PLAYERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_weather():
    if not WEATHER_PATH.exists():
        return {}
    with open(WEATHER_PATH, "r", encoding="utf-8") as f:
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
    weather = load_weather()

    a_name = match.player1.lower()
    b_name = match.player2.lower()

    a = players.get(a_name, {})
    b = players.get(b_name, {})

    elo_a = a.get("elo_clay", 1800)
    elo_b = b.get("elo_clay", 1800)

    ace_rate_a = a.get("ace_rate_clay_3y", 0.25)
    ace_rate_b = b.get("ace_rate_clay_3y", 0.25)

    ace_allowed_a = a.get("ace_allowed_clay_3y", 0.22)
    ace_allowed_b = b.get("ace_allowed_clay_3y", 0.22)

    break_rate_a = a.get("break_rate_clay_3y", 0.20)
    break_rate_b = b.get("break_rate_clay_3y", 0.20)

    break_allowed_a = a.get("break_allowed_clay_3y", 0.18)
    break_allowed_b = b.get("break_allowed_clay_3y", 0.18)

    p_a = win_prob(elo_a, elo_b)
    p_b = 1 - p_a

    c_factor = court_factor(match.court)
    madrid_factor = 1.15
    match_length = 1.08 + (1 - abs(p_a - 0.5)) * 0.5

    day_weather = weather.get(match.date, {})
    avg_temp = day_weather.get("avg_temp")
    wind_kmh = day_weather.get("wind_kmh")

    ace_wf = ace_weather_factor(avg_temp, wind_kmh)
    break_wf = break_weather_factor(avg_temp, wind_kmh)

    sim_a = find_similar_players(a_name, players, top_n=3)
    sim_b = find_similar_players(b_name, players, top_n=3)

    sim_boost_a = 1.0 + (0.01 * len(sim_a))
    sim_boost_b = 1.0 + (0.01 * len(sim_b))

    aces_a = round(((ace_rate_a + ace_allowed_b) / 2) * 20 * c_factor * madrid_factor * match_length * ace_wf * sim_boost_a, 1)
    aces_b = round(((ace_rate_b + ace_allowed_a) / 2) * 20 * c_factor * madrid_factor * match_length * ace_wf * sim_boost_b, 1)

    breaks_a = round(((break_rate_a + break_allowed_b) / 2) * 10 * (1.12 - (c_factor - 1) * 0.5) * break_wf, 1)
    breaks_b = round(((break_rate_b + break_allowed_a) / 2) * 10 * (1.12 - (c_factor - 1) * 0.5) * break_wf, 1)

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
        "match_length": round(match_length, 2),
        "avg_temp": avg_temp,
        "wind_kmh": wind_kmh,
        "ace_weather_factor": ace_wf,
        "break_weather_factor": break_wf
    }

    return result, context
