import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def fetch_tennis_elo(player_name):
    ua = UserAgent()
    headers = {'User-Agent': ua.random}

    search_url = f"https://www.ultimatetennisstatistics.com/searchPlayer?searchTerm={player_name.replace(' ', '%20')}"
    try:
        res = requests.get(search_url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "lxml")
        rows = soup.select("table tbody tr")

        if not rows:
            return {"player": player_name, "elo": None, "error": "No match"}

        cells = rows[0].find_all("td")
        if len(cells) >= 4:
            return {
                "player": player_name,
                "elo": cells[2].text.strip(),
                "surface_strength": cells[3].text.strip()
            }

        return {"player": player_name, "elo": None, "error": "Bad format"}
    except Exception as e:
        return {"player": player_name, "elo": None, "error": str(e)}
