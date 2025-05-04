import requests
from bs4 import BeautifulSoup

def scrape_rotowire_data():
    try:
        url = "https://www.rotowire.com/injury-report.php"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.select("table.injury-table tbody tr")

        injury_info = {}
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue
            team = cols[0].text.strip()
            player = cols[1].text.strip()
            status = cols[4].text.strip()

            if team not in injury_info:
                injury_info[team] = []
            injury_info[team].append({"player": player, "status": status})

        return injury_info

    except Exception as e:
        print(f"[rotowire scraper] ERROR: {e}")
        return {}
