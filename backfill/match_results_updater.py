import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo


OUT_DIR = Path("data/live")
MATCHES_PATH = OUT_DIR / "matches.json"
RESULTS_PATH = OUT_DIR / "match_results.json"


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
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def make_result_key(row):
    return (
        row.get("date"),
        row.get("match")
    )


def dedupe_results(rows):
    seen = set()
    output = []

    for row in rows:
        key = make_result_key(row)
        if key in seen:
            continue

        seen.add(key)
        output.append(row)

    return output


def estimate_result_from_prediction_placeholder(match):
    """
    Placeholder tecnico.

    In B21 lo sostituiremo con parsing stats ufficiali.
    Per ora NON inventiamo risultati: ritorna None.
    """
    return None


def update_match_results():
    matches = safe_load_json(MATCHES_PATH, [])
    existing = safe_load_json(RESULTS_PATH, [])

    new_results = []

    for m in matches:
        match_name = f"{m.get('player1')} vs {m.get('player2')}"

        already_exists = any(
            r.get("date") == m.get("date")
            and r.get("match") == match_name
            for r in existing
        )

        if already_exists:
            continue

        result = estimate_result_from_prediction_placeholder(m)

        if result is None:
            continue

        new_results.append(result)

    combined = dedupe_results(existing + new_results)
    safe_write_json(RESULTS_PATH, combined)

    debug = {
        "updated_at": datetime.now(ZoneInfo("Europe/Madrid")).isoformat(),
        "existing_count": len(existing),
        "new_results_count": len(new_results),
        "final_count": len(combined),
        "status": "placeholder_no_official_stats_yet"
    }

    safe_write_json(OUT_DIR / "match_results_debug.json", debug)

    return debug
