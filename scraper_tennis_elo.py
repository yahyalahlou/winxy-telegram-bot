import requests
from bs4 import BeautifulSoup

def scrape_tennis_elo_data():
    try:
        url = "https://tennisabstract.com/recent_elo.html"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        players = []
        for row in soup.select("table tr")[1:]:
            cols = row.find_all("td")
            if len(cols) >= 3:
                name = cols[0].text.strip()
                elo = cols[2].text.strip()
                players.append({"name": name, "elo": elo})

        return {"elo_ratings": players}

    except Exception as e:
        print(f"[tennis elo scraper] ERROR: {e}")
        return {}
