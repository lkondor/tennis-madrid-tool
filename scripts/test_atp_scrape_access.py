import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


TEST_URLS = [
    "https://www.atptour.com/en/scores/stats-centre/archive/2026/1536/ms016",
    "https://www.atptour.com/en/scores/stats-centre/archive/2025/544/qs019",
]


def fetch(url):
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; tennis-tool/1.0; personal research)",
            "Accept": "text/html,application/xhtml+xml",
        },
    )

    try:
        with urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8", errors="ignore")
            print(f"OK {response.status}: {url}")
            print(f"HTML length: {len(html)}")
            print(f"Contains Aces: {'Aces' in html}")
            print(f"Contains ServiceGamesPlayed: {'ServiceGamesPlayed' in html}")
            print("-" * 80)
    except HTTPError as e:
        print(f"HTTP ERROR {e.code}: {url}")
    except URLError as e:
        print(f"URL ERROR: {e.reason}")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    for url in TEST_URLS:
        fetch(url)
        time.sleep(3)
