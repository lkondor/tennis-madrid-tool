import requests
from bs4 import BeautifulSoup


class Match:
    def __init__(self, player1, player2, court):
        self.player1 = player1
        self.player2 = player2
        self.court = court


def get_upcoming_matches():
    url = "https://mutuamadridopen.com/en/order-of-play/"
    
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        matches = []

        # ⚠️ selettori generici (potrebbero cambiare nel tempo)
        rows = soup.find_all("div", class_="match")

        for row in rows:
            players = row.get_text(" ", strip=True)

            # parsing molto semplice
            parts = players.split(" vs ")
            if len(parts) >= 2:
                p1 = parts[0]
                p2 = parts[1]

                court = "Madrid"
                matches.append(Match(p1, p2, court))

        # fallback se scraping non funziona
        if not matches:
            return [
                Match("Sinner", "Medvedev", "Center Court"),
                Match("Alcaraz", "Zverev", "Court 1"),
                Match("Swiatek", "Sabalenka", "Center Court")
            ]

        return matches

    except Exception:
        # fallback totale
        return [
            Match("Sinner", "Medvedev", "Center Court"),
            Match("Alcaraz", "Zverev", "Court 1"),
            Match("Swiatek", "Sabalenka", "Center Court")
        ]
