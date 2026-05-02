import json
from pathlib import Path
from datetime import datetime


LIVE_IMPORT_DIR = Path("data/raw/imports_live")
HISTORICAL_PATH = Path("data/raw/historical_matches.json")


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


def norm(x):
    return str(x or "").lower().strip()


def is_singles(row):
    name1 = norm(row.get("player1"))
    name2 = norm(row.get("player2"))

    markers = ["/", "&", " and ", "+"]

    for m in markers:
        if m in name1 or m in name2:
            return False

    return True


def make_id(row):
    return "|".join([
        str(row.get("date")),
        str(row.get("tournament_slug")),
        str(row.get("player1")),
        str(row.get("player2")),
        str(row.get("round")),
    ])


def import_live_matches():
    historical = load_json(HISTORICAL_PATH, [])
    existing_ids = {make_id(r) for r in historical}

    new_rows = []

    if not LIVE_IMPORT_DIR.exists():
        print("No live import directory found.")
        return

    for file in LIVE_IMPORT_DIR.iterdir():
        if file.suffix != ".json":
            continue

        data = load_json(file, [])

        print(f"Reading {file.name} -> {len(data)} rows")

        for row in data:
            if not is_singles(row):
                continue

            row_id = make_id(row)

            if row_id in existing_ids:
                continue

            row["source"] = "live_import"
            row["imported_at"] = datetime.utcnow().isoformat()

            new_rows.append(row)
            existing_ids.add(row_id)

    combined = historical + new_rows

    save_json(HISTORICAL_PATH, combined)

    print(f"Added {len(new_rows)} new matches")
    print(f"Total matches: {len(combined)}")


if __name__ == "__main__":
    import_live_matches()
