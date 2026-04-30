import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, deque


HISTORICAL_MATCHES_PATH = Path("data/raw/historical_matches.json")
CURRENT_RESULTS_PATH = Path("data/live/current_tournament_results.json")
TOURNAMENT_CONTEXT_PATH = Path("data/live/tournament_context.json")
PLAYERS_OUTPUT_PATH = Path("data/live/players.json")


DEFAULT_CONTEXT = {
    "tournament": "Madrid Open",
    "slug": "madrid",
    "season": 2026,
    "surface": "clay",
    "tour": "combined",
    "location": "Madrid",
    "altitude_m": 667,
    "lookback_tournament_editions": [2023, 2024, 2025],
    "current_edition": 2026,
}


def load_json(path, default):
    if not path.exists():
        return default

    try:
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            return default
        return json.loads(text)
    except Exception:
        return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def norm_name(name):
    return str(name).lower().strip()


def safe_div(num, den, default=0.0):
    return round(num / den, 4) if den else default


def is_same_tour(match_tour, target_tour):
    if target_tour == "combined":
        return match_tour in ["atp", "wta", "combined", None, ""]
    return match_tour == target_tour


def get_player_side(match, player):
    p1 = norm_name(match.get("player1"))
    p2 = norm_name(match.get("player2"))
    player = norm_name(player)

    if player == p1:
        return "p1"
    if player == p2:
        return "p2"

    return None


def get_opponent(match, player):
    side = get_player_side(match, player)

    if side == "p1":
        return norm_name(match.get("player2"))
    if side == "p2":
        return norm_name(match.get("player1"))

    return None


def extract_player_match_stats(match, player):
    side = get_player_side(match, player)

    if side is None:
        return None

    if side == "p1":
        own = "p1"
        opp = "p2"
    else:
        own = "p2"
        opp = "p1"

    return {
        "aces": match.get(f"aces_{own}", 0) or 0,
        "aces_allowed": match.get(f"aces_{opp}", 0) or 0,
        "breaks": match.get(f"breaks_{own}", 0) or 0,
        "breaks_allowed": match.get(f"breaks_{opp}", 0) or 0,
        "service_games": match.get(f"service_games_{own}", 0) or 0,
        "return_games": match.get(f"return_games_{own}", 0) or 0,
        "winner": norm_name(match.get("winner")),
        "player": norm_name(player),
        "opponent": get_opponent(match, player),
        "court": norm_name(match.get("court")),
        "surface": norm_name(match.get("surface")),
        "tournament_slug": norm_name(match.get("tournament_slug")),
        "season": match.get("season"),
        "date": match.get("date"),
        "tour": norm_name(match.get("tour")),
        "avg_temp": match.get("avg_temp"),
        "wind_kmh": match.get("wind_kmh"),
    }


def empty_bucket():
    return {
        "matches": 0,
        "aces": 0,
        "aces_allowed": 0,
        "breaks": 0,
        "breaks_allowed": 0,
        "service_games": 0,
        "return_games": 0,
        "wins": 0,
    }


def add_to_bucket(bucket, stats):
    bucket["matches"] += 1
    bucket["aces"] += stats["aces"]
    bucket["aces_allowed"] += stats["aces_allowed"]
    bucket["breaks"] += stats["breaks"]
    bucket["breaks_allowed"] += stats["breaks_allowed"]
    bucket["service_games"] += stats["service_games"]
    bucket["return_games"] += stats["return_games"]

    if stats["winner"] == stats["player"]:
        bucket["wins"] += 1


def summarize_bucket(bucket):
    return {
        "matches": bucket["matches"],
        "ace_rate": safe_div(bucket["aces"], bucket["service_games"]),
        "ace_allowed": safe_div(bucket["aces_allowed"], bucket["return_games"]),
        "break_rate": safe_div(bucket["breaks"], bucket["return_games"]),
        "break_allowed": safe_div(bucket["breaks_allowed"], bucket["service_games"]),
        "win_rate": safe_div(bucket["wins"], bucket["matches"]),
    }


def estimate_elo_from_win_rate(win_rate, base=1800):
    return round(base + ((win_rate - 0.5) * 400))


def infer_data_quality(surface_matches, tournament_matches, current_matches):
    if surface_matches >= 15:
        return "historical_match_stats"

    if surface_matches >= 5 or tournament_matches >= 3:
        return "partial_historical"

    if current_matches >= 1:
        return "current_tournament_only"

    return "synthetic"


def build_player_stats():
    context = load_json(TOURNAMENT_CONTEXT_PATH, DEFAULT_CONTEXT)

    tournament_slug = norm_name(context.get("slug", "madrid"))
    surface = norm_name(context.get("surface", "clay"))
    target_tour = norm_name(context.get("tour", "combined"))
    season = int(context.get("season", 2026))
    lookback_editions = context.get(
        "lookback_tournament_editions",
        [season - 3, season - 2, season - 1],
    )

    historical_matches = load_json(HISTORICAL_MATCHES_PATH, [])
    current_results = load_json(CURRENT_RESULTS_PATH, [])

    all_matches = historical_matches + current_results

    players = set()

    for m in all_matches:
        if not is_same_tour(norm_name(m.get("tour")), target_tour):
            continue

        if norm_name(m.get("player1")):
            players.add(norm_name(m.get("player1")))

        if norm_name(m.get("player2")):
            players.add(norm_name(m.get("player2")))

    output = {}

    for player in sorted(players):
        surface_bucket = empty_bucket()
        tournament_bucket = empty_bucket()
        current_bucket = empty_bucket()

        recent_results = deque(maxlen=10)
        surface_results = deque(maxlen=20)

        court_buckets = defaultdict(empty_bucket)
        weather_buckets = {
            "hot": empty_bucket(),
            "windy": empty_bucket(),
            "cool": empty_bucket(),
        }

        player_tour = None

        for m in all_matches:
            match_tour = norm_name(m.get("tour"))

            if not is_same_tour(match_tour, target_tour):
                continue

            if player not in [norm_name(m.get("player1")), norm_name(m.get("player2"))]:
                continue

            stats = extract_player_match_stats(m, player)

            if not stats:
                continue

            player_tour = match_tour or player_tour

            match_surface = norm_name(m.get("surface"))
            match_slug = norm_name(m.get("tournament_slug"))
            match_season = m.get("season")

            is_current_result = m in current_results

            if match_surface == surface and match_season >= season - 3:
                add_to_bucket(surface_bucket, stats)

                surface_results.append(
                    1 if stats["winner"] == stats["player"] else 0
                )

            if (
                match_slug == tournament_slug
                and match_season in lookback_editions
            ):
                add_to_bucket(tournament_bucket, stats)

            if is_current_result and match_slug == tournament_slug:
                add_to_bucket(current_bucket, stats)

                if stats["court"]:
                    add_to_bucket(court_buckets[stats["court"]], stats)

                avg_temp = stats.get("avg_temp")
                wind_kmh = stats.get("wind_kmh")

                if avg_temp is not None and avg_temp >= 26:
                    add_to_bucket(weather_buckets["hot"], stats)

                if avg_temp is not None and avg_temp <= 18:
                    add_to_bucket(weather_buckets["cool"], stats)

                if wind_kmh is not None and wind_kmh >= 15:
                    add_to_bucket(weather_buckets["windy"], stats)

            recent_results.append(
                1 if stats["winner"] == stats["player"] else 0
            )

        surface_summary = summarize_bucket(surface_bucket)
        tournament_summary = summarize_bucket(tournament_bucket)
        current_summary = summarize_bucket(current_bucket)

        recent_form_10 = (
            round(sum(recent_results) / len(recent_results), 4)
            if recent_results
            else 0.5
        )

        surface_form_20 = (
            round(sum(surface_results) / len(surface_results), 4)
            if surface_results
            else 0.5
        )

        live_weight = min(0.25, current_summary["matches"] * 0.08)

        base_win_rate = (
            surface_summary["win_rate"] * 0.65
            + tournament_summary["win_rate"] * 0.25
            + current_summary["win_rate"] * live_weight
        )

        if base_win_rate <= 0:
            base_win_rate = 0.5

        elo_surface = estimate_elo_from_win_rate(base_win_rate)

        data_quality = infer_data_quality(
            surface_summary["matches"],
            tournament_summary["matches"],
            current_summary["matches"],
        )

        output[player] = {
            "tour": player_tour or target_tour,
            "surface": surface,
            "tournament_slug": tournament_slug,

            # campi generici nuovi
            "elo_surface": elo_surface,

            "ace_rate_surface_3y": surface_summary["ace_rate"],
            "ace_allowed_surface_3y": surface_summary["ace_allowed"],
            "break_rate_surface_3y": surface_summary["break_rate"],
            "break_allowed_surface_3y": surface_summary["break_allowed"],

            "tournament_ace_rate_3ed": tournament_summary["ace_rate"],
            "tournament_ace_allowed_3ed": tournament_summary["ace_allowed"],
            "tournament_break_rate_3ed": tournament_summary["break_rate"],
            "tournament_break_allowed_3ed": tournament_summary["break_allowed"],

            "current_tournament_ace_rate": current_summary["ace_rate"],
            "current_tournament_ace_allowed": current_summary["ace_allowed"],
            "current_tournament_break_rate": current_summary["break_rate"],
            "current_tournament_break_allowed": current_summary["break_allowed"],
            "current_tournament_matches": current_summary["matches"],

            "recent_form_10": recent_form_10,
            "surface_form_20": surface_form_20,

            "court_adjustments": {
                court: summarize_bucket(bucket)
                for court, bucket in court_buckets.items()
                if bucket["matches"] > 0
            },

            "weather_adjustments": {
                key: summarize_bucket(bucket)
                for key, bucket in weather_buckets.items()
                if bucket["matches"] > 0
            },

            "data_quality": data_quality,
            "updated_at": datetime.utcnow().isoformat(),

            # campi legacy per non rompere model_service.py
            "elo_clay": elo_surface if surface == "clay" else None,
            "ace_rate_clay_3y": surface_summary["ace_rate"] if surface == "clay" else None,
            "ace_allowed_clay_3y": surface_summary["ace_allowed"] if surface == "clay" else None,
            "break_rate_clay_3y": surface_summary["break_rate"] if surface == "clay" else None,
            "break_allowed_clay_3y": surface_summary["break_allowed"] if surface == "clay" else None,
            "madrid_ace_rate": tournament_summary["ace_rate"] if tournament_slug == "madrid" else None,
            "madrid_break_rate": tournament_summary["break_rate"] if tournament_slug == "madrid" else None,
        }

    save_json(PLAYERS_OUTPUT_PATH, output)

    print(f"Generated {len(output)} players")
    print(f"Output: {PLAYERS_OUTPUT_PATH}")


if __name__ == "__main__":
    build_player_stats()
