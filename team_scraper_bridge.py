import logging
from scraper_flashscore import get_flashscore_matches
from scraper_rotowire import get_injury_status
from scraper_tennis_elo import get_elo_strength


def get_team_factors(team_1, team_2, sport):
    """
    Central scraper logic for WinxyBot Agent. Returns dict of:
    - momentum: strong/neutral/weak
    - injury: none/minor/severe
    - fatigue: low/medium/high
    """
    data = {
        "momentum": "neutral",
        "injury": "none",
        "fatigue": "medium"
    }

    try:
        # 🚨 INJURY LOGIC (NBA via RotoWire)
        if sport.lower() == "basketball":
            injury_status = get_injury_status(team_1)
            if "out" in injury_status.lower():
                data["injury"] = "severe"
            elif "questionable" in injury_status.lower():
                data["injury"] = "minor"

        # ⚾️ MOMENTUM/FATIGUE via FlashScore
        matches = get_flashscore_matches()
        team_matches = [m for m in matches if team_1.lower() in str(m).lower()]

        if len(team_matches) >= 3:
            data["momentum"] = "strong"
            data["fatigue"] = "high"
        elif len(team_matches) == 1:
            data["momentum"] = "weak"
            data["fatigue"] = "low"

        # 🎾 TENNIS ELO (only applies if sport = tennis)
        if sport.lower() == "tennis":
            team1_score = get_elo_strength(team_1)
            team2_score = get_elo_strength(team_2)
            if team1_score and team2_score:
                if int(team1_score) > int(team2_score):
                    data["momentum"] = "strong"
                else:
                    data["momentum"] = "weak"

    except Exception as err:
        logging.warning(f"[Scraper Bridge] Fallback mode. Error: {err}")

    return data
