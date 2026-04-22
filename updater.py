import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from backfill.elo import SurfaceElo
from backfill.atp_backfill import build_atp_player_backfill
from backfill.wta_backfill import aggregate_wta_players_from_matches
from backfill.aggregate_players import build_three_year_rates


OUT_DIR = Path("data/live")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_official_results_history():
    path = OUT_DIR / "results_history.json"
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_clay_elo(results_history):
    elo = SurfaceElo(base_rating=1500, k=24)

    clay_results = [
        r for r in results_history
        if r.get("surface", "").lower() == "clay"
        and str(r.get("date", ""))[:4] in ["2023", "2024", "2025", "2026"]
    ]

    clay_results.sort(key=lambda x: x["date"])

    for r in clay_results:
        winner = r["winner"]
        loser = r["loser"]
        elo.update(winner, loser)

    return elo.export()


def merge_players(atp_players, wta_players, elo_map):
    merged = {}

    for name, rec in atp_players.items():
        merged[name] = build_three_year_rates(rec)

    for name, rec in wta_players.items():
        merged[name] = build_three_year_rates(rec)

    for name, rating in elo_map.items():
        merged.setdefault(name, {})
        merged[name]["elo_clay"] = round(rating, 1)

    return merged


def main():
    results_history = load_official_results_history()
    elo_map = compute_clay_elo(results_history)

    atp_players = build_atp_player_backfill()
    wta_players = aggregate_wta_players_from_matches()

    players = merge_players(atp_players, wta_players, elo_map)

    with open(OUT_DIR / "players.json", "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

    with open(OUT_DIR / "meta.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    meta["players_backfill_updated_at"] = datetime.now(ZoneInfo("Europe/Madrid")).isoformat()

    with open(OUT_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
