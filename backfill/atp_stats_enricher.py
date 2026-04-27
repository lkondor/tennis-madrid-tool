import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup


OUT_DIR = Path("data/live")
DEBUG_PATH = OUT_DIR / "atp_stats_enricher_debug.json"
OUTPUT_PATH = OUT_DIR / "atp_enriched_stats.json"

MADRID_TZ = ZoneInfo("Europe/Madrid")

ATP_STATS_URLS = {
    "stats_home": "https://www.atptour.com/en/stats/stats-home",
    "individual_game_stats": "https://www.atptour.com/en/stats/individual-game-stats",
    "leaderboard": "https://www.atptour.com/en/stats/leaderboard",
    "tdi_leaderboard": "https://www.atptour.com/en/stats/tdi-leaderboard",
}


KEYWORDS = [
    "Aces",
    "1st Serve",
    "1st Serve Points Won",
    "2nd Serve Points Won",
    "Service Games Won",
    "Break Points Saved",
    "Break Points Converted",
    "Return Games Won",
    "Serve Quality",
    "Return Quality",
    "Shot Quality",
]


def safe_write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def safe_get(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; MadridPredictor/1.0; +https://github.com)"
        )
    }
    return requests.get(url, headers=headers, timeout=25)


def clean_line(line):
    return " ".join(str(line).replace("\xa0", " ").split()).strip()


def inspect_page(name, url):
    debug = {
        "name": name,
        "url": url,
        "http_status": None,
        "line_count": 0,
        "sample_lines": [],
        "keyword_hits": {},
        "sample_classes": [],
        "status": "not_started",
        "error": None,
    }

    try:
        response = safe_get(url)
        debug["http_status"] = response.status_code

        if response.status_code != 200:
            debug["status"] = "http_error"
            return debug

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text("\n", strip=True)

        lines = [
            clean_line(x)
            for x in text.splitlines()
            if clean_line(x)
        ]

        debug["line_count"] = len(lines)
        debug["sample_lines"] = lines[:150]

        for kw in KEYWORDS:
            debug["keyword_hits"][kw] = sum(
                1 for line in lines
                if kw.lower() in line.lower()
            )

        debug["sample_classes"] = sorted(
            list({
                c
                for tag in soup.find_all(True)
                for c in (tag.get("class") or [])
            })
        )[:200]

        debug["status"] = "ok"

        return debug

    except Exception as exc:
        debug["status"] = "exception"
        debug["error"] = str(exc)
        return debug


def update_atp_enriched_stats():
    pages = []

    for name, url in ATP_STATS_URLS.items():
        pages.append(inspect_page(name, url))

    debug = {
        "updated_at": datetime.now(MADRID_TZ).isoformat(),
        "pages": pages,
    }

    safe_write_json(DEBUG_PATH, debug)

    # Per ora non produciamo stats finché non sappiamo quale pagina/API è parsabile.
    output = {
        "updated_at": datetime.now(MADRID_TZ).isoformat(),
        "status": "debug_only",
        "players": {}
    }

    safe_write_json(OUTPUT_PATH, output)

    return {
        "status": "debug_only",
        "pages_checked": len(pages),
    }
