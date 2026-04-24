import json
import random
from datetime import datetime, timedelta
from pathlib import Path


OUT_DIR = Path("data/live")
RESULTS_PATH = OUT_DIR / "results_history.json"
ALIASES_PATH = OUT_DIR / "player_aliases.json"
UNRESOLVED_PATH = OUT_DIR / "unresolved_players.json"


def safe_load_json(path, default):
    try:
        if not path.exists():
            return default
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            return default
        return json.loads(text)
    except Exception:
        return default


def safe_write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_name(name):
    return str(name).lower().strip()


def canonical_name(name, aliases):
    key = normalize_name(name)
    return normalize_name(aliases.get(key, key))


def random_date():
    base = datetime(2024, 1, 1)
    return (base + timedelta(days=random.randint(0, 500))).date().isoformat()


def player_profile(name):
    """
    Profilo sintetico differenziato per validazione modello.
    Non è ancora dato ufficiale, ma evita valori uguali.
    """
    name = normalize_name(name)
    seed = sum(ord(c) for c in name)
    random.seed(seed)

    serve_level = random.uniform(0.35, 0.95)
    return_level = random.uniform(0.15, 0.55)
    clay_strength = random.uniform(0.35, 0.85)

    return {
        "serve": serve_level,
        "return": return_level,
        "clay": clay_strength,
    }


def generate_match(p1, p2):
    prof1 = player_profile(p1)
    prof2 = player_profile(p2)

    rating1 = prof1["clay"] + prof1["return"] * 0.4 + prof1["serve"] * 0.2
    rating2 = prof2["clay"] + prof2["return"] * 0.4 + prof2["serve"] * 0.2

    p1_win_prob = rating1 / (rating1 + rating2)

    if random.random() < p1_win_prob:
        winner, loser = p1, p2
    else:
        winner, loser = p2, p1

    aces_p1 = max(0, round(random.gauss(prof1["serve"] * 10, 2)))
    aces_p2 = max(0, round(random.gauss(prof2["serve"] * 10, 2)))

    service_games_p1 = random.randint(10, 14)
    service_games_p2 = random.randint(10, 14)

    breaks_p1 = max(0, round(random.gauss(prof1["return"] * 6, 1)))
    breaks_p2 = max(0, round(random.gauss(prof2["return"] * 6, 1)))

    return {
        "date": random_date(),
        "tour": "Synthetic",
        "tournament": "Synthetic Clay",
        "surface": "Clay",
        "player1": p1.title(),
        "player2": p2.title(),
        "winner": winner.title(),
        "loser": loser.title(),
        "aces_p1": aces_p1,
        "aces_p2": aces_p2,
        "service_games_p1": service_games_p1,
        "service_games_p2": service_games_p2,
        "breaks_p1": breaks_p1,
        "breaks_p2": breaks_p2,
        "return_games_p1": service_games_p2,
        "return_games_p2": service_games_p1,
        "data_source": "synthetic_validation",
        "stats_quality": "synthetic"
    }


def result_key(row):
    return (
        row.get("date", ""),
        normalize_name(row.get("player1", "")),
        normalize_name(row.get("player2", "")),
        normalize_name(row.get("tournament", "")),
    )


def dedupe_results(rows):
    seen = set()
    output = []

    for row in rows:
        key = result_key(row)
        rev = (
            row.get("date", ""),
            normalize_name(row.get("player2", "")),
            normalize_name(row.get("player1", "")),
            normalize_name(row.get("tournament", "")),
        )

        if key in seen or rev in seen:
            continue

        seen.add(key)
        output.append(row)

    return output


def expand_history():
    data = safe_load_json(RESULTS_PATH, [])
    aliases = safe_load_json(ALIASES_PATH, {})
    unresolved = safe_load_json(UNRESOLVED_PATH, [])

    existing_players = set()
    for m in data:
        existing_players.add(normalize_name(m.get("player1", "")))
        existing_players.add(normalize_name(m.get("player2", "")))

    unresolved_players = [
        canonical_name(p, aliases)
        for p in unresolved
    ]

    all_players = sorted(set(existing_players) | set(unresolved_players))

    if len(all_players) < 2:
        safe_write_json(RESULTS_PATH, data)
        return {
            "added_matches": 0,
            "total_matches": len(data)
        }

    new_matches = []

    for player in unresolved_players:
        if not player:
            continue

        opponents = [p for p in all_players if p != player]
        random.shuffle(opponents)
        opponents = opponents[:8]

        for opp in opponents:
            for _ in range(4):
                new_matches.append(generate_match(player, opp))

    combined = dedupe_results(data + new_matches)
    safe_write_json(RESULTS_PATH, combined)

    return {
        "added_matches": len(combined) - len(data),
        "total_matches": len(combined)
    }
