import requests
from bs4 import BeautifulSoup


def scrape_atp_results():
    url = "https://www.atptour.com/en/scores/results-archive"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    # qui devi iterare per torneo → match → stats
    # ogni match → append a results_history.json

    return []
