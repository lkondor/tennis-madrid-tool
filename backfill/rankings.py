import requests
from bs4 import BeautifulSoup


def get_atp_top_players(limit=150):
    url = "https://www.atptour.com/en/rankings/singles"
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text("\n", strip=True)
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        players = []
        for line in lines:
            if len(players) >= limit:
                break
            if len(line.split()) >= 2 and not any(ch.isdigit() for ch in line):
                players.append(line.title())
        return players[:limit]
    except Exception:
        return []


def get_wta_top_players(limit=150):
    url = "https://www.wtatennis.com/rankings/singles"
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text("\n", strip=True)
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        players = []
        for line in lines:
            if len(players) >= limit:
                break
            if len(line.split()) >= 2 and not any(ch.isdigit() for ch in line):
                players.append(line.title())
        return players[:limit]
    except Exception:
        return []
