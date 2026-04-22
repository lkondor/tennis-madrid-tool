import io
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None


@dataclass
class Match:
    player1: str
    player2: str
    court: str


DEMO_MATCHES = [
    Match("Sinner", "Medvedev", "Manolo Santana Stadium"),
    Match("Alcaraz", "Zverev", "Arantxa Sanchez Stadium"),
    Match("Swiatek", "Sabalenka", "Court 4"),
]


COURT_NAMES = [
    "MANOLO SANTANA STADIUM",
    "ARANTXA SANCHEZ STADIUM",
    "STADIUM 3",
    "COURT 3",
    "COURT 4",
    "COURT 5",
    "COURT 6",
    "COURT 7",
    "COURT 8",
]


def _candidate_pdf_urls():
    madrid_now = datetime.now(ZoneInfo("Europe/Madrid")).date()

    # prima domani, poi oggi
    days = [madrid_now + timedelta(days=1), madrid_now]

    urls = []
    for d in days:
        urls.append(
            f"https://mutuamadridopen.com/wp-content/uploads/{d.year}/{d.month:02d}/OP-{d.year}-{d.month:02d}-{d.day:02d}.pdf"
        )
    return urls


def _download_pdf_text(url: str) -> str:
    if PdfReader is None:
        return ""

    try:
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            return ""

        content_type = r.headers.get("content-type", "").lower()
        if "pdf" not in content_type:
            return ""

        reader = PdfReader(io.BytesIO(r.content))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        return ""


def _clean_line(line: str) -> str:
    line = line.replace("\xa0", " ").strip()
    line = re.sub(r"\[[^\]]+\]", "", line)
    line = re.sub(r"\([A-Z]{2,3}\)", "", line)
    line = re.sub(r"\s+", " ", line).strip(" -–•")
    return line


def _is_player_name(line: str) -> bool:
    if not line:
        return False
    if any(ch.isdigit() for ch in line):
        return False

    words = line.split()
    if len(words) < 2 or len(words) > 5:
        return False

    banned = {
        "ORDER", "PLAY", "MADRID", "OPEN", "COURT", "STADIUM",
        "FOLLOWED", "STARTING", "NOT", "BEFORE", "SINGLES", "DOUBLES"
    }
    if any(w.upper() in banned for w in words):
        return False

    letters = [c for c in line if c.isalpha()]
    if not letters:
        return False

    upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    return upper_ratio > 0.5


def _extract_matches(text: str):
    lines = [_clean_line(x) for x in text.splitlines()]
    lines = [x for x in lines if x]

    matches = []
    current_court = "Madrid"
    buffer_names = []

    for line in lines:
        upper = line.upper()

        if upper in COURT_NAMES:
            current_court = line.title()
            buffer_names = []
            continue

        if _is_player_name(line):
            buffer_names.append(line.title())

            if len(buffer_names) == 2:
                p1, p2 = buffer_names
                if p1 != p2:
                    matches.append(Match(p1, p2, current_court))
                buffer_names = []
        else:
            buffer_names = []

    deduped = []
    seen = set()
    for m in matches:
        key = (m.player1.lower(), m.player2.lower(), m.court.lower())
        rev = (m.player2.lower(), m.player1.lower(), m.court.lower())
        if key not in seen and rev not in seen:
            seen.add(key)
            deduped.append(m)

    return deduped


def get_upcoming_matches():
    for url in _candidate_pdf_urls():
        text = _download_pdf_text(url)
        if not text:
            continue

        matches = _extract_matches(text)
        if matches:
            return matches

    return DEMO_MATCHES


load_matches = get_upcoming_matches
