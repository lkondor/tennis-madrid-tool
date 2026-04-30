import json
from pathlib import Path
from datetime import datetime


TRACKING_PATH = Path("data/live/bet_tracking.json")
RESULTS_PATH = Path("data/live/match_results.json")


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


def save_json(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_tracking():
    return load_json(TRACKING_PATH, [])


def save_tracking(rows):
    save_json(TRACKING_PATH, rows)


def load_match_results():
    return load_json(RESULTS_PATH, [])


def make_pick_id(date, match, market, line):
    return f"{date}|{match}|{market}|{line}"


def normalize_market(market):
    market = str(market).strip()

    if market in ["Best Over Ace", "Over Ace"]:
        return "Over Ace"

    if market in ["Best Over Break", "Over Break"]:
        return "Over Break"

    return market


def add_picks(date, portfolio_rows):
    existing = load_tracking()
    existing_ids = {r.get("pick_id") for r in existing}

    new_rows = []

    for p in portfolio_rows:
        pick_id = make_pick_id(
            date=date,
            match=p["Match"],
            market=p["Market"],
            line=p["Line"],
        )

        if pick_id in existing_ids:
            continue

        new_rows.append(
            {
                "pick_id": pick_id,
                "created_at": datetime.utcnow().isoformat(),
                "date": date,
                "match": p["Match"],
                "court": p.get("Court"),
                "market": p["Market"],
                "market_type": normalize_market(p["Market"]),
                "line": p["Line"],
                "model_prob": p.get("Model Prob"),
                "edge": p.get("Edge"),
                "ev": p.get("EV"),
                "confidence": p.get("Confidence"),
                "confidence_score": p.get("Confidence score"),
                "status": "PENDING",
                "actual_value": None,
                "notes": "",
            }
        )

    combined = existing + new_rows
    save_tracking(combined)

    return len(new_rows)


def auto_settle_picks():
    tracking_rows = load_tracking()
    results = load_match_results()

    result_map = {
        (r.get("date"), r.get("match")): r
        for r in results
    }

    updated = 0

    for pick in tracking_rows:
        if pick.get("status") != "PENDING":
            continue

        key = (pick.get("date"), pick.get("match"))
        result = result_map.get(key)

        if not result:
            continue

        market_type = pick.get("market_type") or normalize_market(pick.get("market"))
        line = float(pick.get("line", 0))

        if market_type == "Over Ace":
            actual = result.get("total_aces")
        elif market_type == "Over Break":
            actual = result.get("total_breaks")
        else:
            actual = None

        if actual is None:
            continue

        pick["actual_value"] = actual

        if actual > line:
            pick["status"] = "WIN"
        elif actual < line:
            pick["status"] = "LOSS"
        else:
            pick["status"] = "PUSH"

        pick["updated_at"] = datetime.utcnow().isoformat()
        pick["notes"] = "Auto-settled from match_results.json"
        updated += 1

    save_tracking(tracking_rows)
    return updated


def update_pick_status(pick_id, status, result=None, notes=""):
    rows = load_tracking()

    for r in rows:
        if r.get("pick_id") == pick_id:
            r["status"] = status
            r["actual_value"] = result
            r["notes"] = notes
            r["updated_at"] = datetime.utcnow().isoformat()

    save_tracking(rows)


def tracking_summary(rows):
    settled = [r for r in rows if r.get("status") in ["WIN", "LOSS", "PUSH"]]

    wins = sum(1 for r in settled if r.get("status") == "WIN")
    losses = sum(1 for r in settled if r.get("status") == "LOSS")
    pushes = sum(1 for r in settled if r.get("status") == "PUSH")

    total = len(settled)
    win_rate = wins / total if total else 0

    ev_rows = [
        r for r in rows
        if isinstance(r.get("ev"), (int, float))
    ]

    avg_ev = (
        sum(r["ev"] for r in ev_rows) / len(ev_rows)
        if ev_rows
        else 0
    )

    return {
        "total_picks": len(rows),
        "settled": total,
        "wins": wins,
        "losses": losses,
        "pushes": pushes,
        "win_rate": win_rate,
        "avg_ev": avg_ev,
    }
