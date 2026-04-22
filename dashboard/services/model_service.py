import math


PLAYER_PROFILES = {
    "jannik sinner": {"serve": 8.8, "return": 7.8, "elo": 2120},
    "carlos alcaraz": {"serve": 7.6, "return": 8.7, "elo": 2150},
    "daniil medvedev": {"serve": 8.3, "return": 7.0, "elo": 2050},
    "alexander zverev": {"serve": 8.9, "return": 6.8, "elo": 2010},
    "iga swiatek": {"serve": 5.6, "return": 9.1, "elo": 2230},
    "aryna sabalenka": {"serve": 8.2, "return": 7.4, "elo": 2140},
}


def _default_profile(name: str):
    key = name.lower().strip()
    if key in PLAYER_PROFILES:
        return PLAYER_PROFILES[key]

    seed = sum(ord(c) for c in key if c.isalpha())
    serve = 5.5 + (seed % 35) / 10.0
    ret = 5.0 + ((seed // 7) % 35) / 10.0
    elo = 1700 + (seed % 250)
    return {"serve": serve, "return": ret, "elo": elo}


def _win_prob(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))


def _court_factor(court: str):
    court_l = str(court).lower()
    if "court 4" in court_l:
        return 1.08
    if "manolo" in court_l:
        return 1.02
    if "arantxa" in court_l:
        return 1.01
    return 1.0


def run_prediction(match):
    a = _default_profile(match.player1)
    b = _default_profile(match.player2)

    p_a = _win_prob(a["elo"], b["elo"])
    p_b = 1 - p_a

    court_factor = _court_factor(match.court)
    madrid_factor = 1.15
    surface_factor = 1.05

    match_length = 1.05 + (1 - abs(p_a - 0.5)) * 0.5

    aces_a = round(max(1.0, a["serve"] * (11 - b["return"]) / 5 * court_factor * madrid_factor * match_length / 2), 1)
    aces_b = round(max(1.0, b["serve"] * (11 - a["return"]) / 5 * court_factor * madrid_factor * match_length / 2), 1)

    breaks_a = round(max(0.2, a["return"] * (11 - b["serve"]) / 12 * surface_factor * (1.15 - court_factor / 10)), 1)
    breaks_b = round(max(0.2, b["return"] * (11 - a["serve"]) / 12 * surface_factor * (1.15 - court_factor / 10)), 1)

    result = {
        "playerA": {
            "aces": aces_a,
            "breaks": breaks_a
        },
        "playerB": {
            "aces": aces_b,
            "breaks": breaks_b
        },
        "totals": {
            "aces": round(aces_a + aces_b, 1),
            "breaks": round(breaks_a + breaks_b, 1)
        }
    }

    context = {
        "surface_factor": surface_factor,
        "madrid_factor": madrid_factor,
        "court_factor": court_factor,
        "match_length": round(match_length, 2),
        "elo_a": a["elo"],
        "elo_b": b["elo"],
        "win_prob_a": round(p_a, 3),
        "win_prob_b": round(p_b, 3)
    }

    return result, context
