import random
from datetime import datetime, timedelta
from pathlib import Path
import json


OUT_DIR = Path("data/live")
RESULTS_PATH = OUT_DIR / "results_history.json"


def safe_load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except:
        return default


def safe_write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def random_date():
    base = datetime(2024, 1, 1)
    return (base + timedelta(days=random.randint(0, 500))).date().isoformat()


def generate_match(p1, p2):
    # forza relativa casuale
    strength = random.random()

    if strength > 0.5:
        winner, loser = p1, p2
    else:
        winner, loser = p2, p1

    aces_w = random.randint(3, 12)
    aces_l = random.randint(2, 10)

    sg_w = random.randint(10, 14)
    sg_l = random.randint(10, 14)

    breaks_w = random.randint(2, 5)
    breaks_l = random.randint(1, 3)

    return {
        "date": random_date(),
        "tour": "Simulated",
        "tournament": "Synthetic",
        "surface": "Clay",
        "player1": p1,
        "player2": p2,
        "winner": winner,
        "loser": loser,
        "aces_p1": aces_w if winner == p1 else aces_l,
        "aces_p2": aces_l if winner == p1 else aces_w,
        "service_games_p1": sg_w,
        "service_games_p2": sg_l,
        "breaks_p1": breaks_w if winner == p1 else breaks_l,
        "breaks_p2": breaks_l if winner == p1 else breaks_w,
        "return_games_p1": sg_l,
        "return_games_p2": sg_w
    }


def expand_history():
    data = safe_load_json(RESULTS_PATH, [])

    players = set()
    for m in data:
        players.add(m["player1"])
        players.add(m["player2"])

    players = list(players)

    new_matches = []

    for p in players:
        opponents = random.sample(players, min(5, len(players)))

        for opp in opponents:
            if p == opp:
                continue

            for _ in range(3):
                new_matches.append(generate_match(p, opp))

    combined = data + new_matches

    safe_write_json(RESULTS_PATH, combined)

    print(f"Added {len(new_matches)} matches. Total now: {len(combined)}")
